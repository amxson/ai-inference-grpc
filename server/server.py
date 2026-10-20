"""Bounded gRPC demo service. Bind locally unless a deployment opts in."""

import hmac
import os
from concurrent import futures

import grpc
import ai_inference_pb2 as pb
import ai_inference_pb2_grpc as rpc
from server import ai_engine

MAX_TEXT_BYTES = 16_384
MAX_STREAM_BYTES = 65_536
MAX_STREAM_ITEMS = 64


class AIInferenceServicer(rpc.AIInferenceServicer):
    def __init__(self, api_token=None):
        self.api_token = (
            os.getenv("GRPC_API_TOKEN", "") if api_token is None else api_token
        )

    def authorize(self, context):
        if self.api_token:
            supplied = dict(context.invocation_metadata()).get("authorization", "")
            if not hmac.compare_digest(
                supplied.encode(), f"Bearer {self.api_token}".encode()
            ):
                context.abort(
                    grpc.StatusCode.UNAUTHENTICATED, "Valid bearer token required."
                )

    @staticmethod
    def validate(text, context):
        if not text.strip():
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, "Text must not be blank.")
        if len(text.encode("utf-8")) > MAX_TEXT_BYTES:
            context.abort(
                grpc.StatusCode.RESOURCE_EXHAUSTED, "Text exceeds the byte limit."
            )

    def AnalyzeSentiment(self, request, context):
        self.authorize(context)
        self.validate(request.text, context)
        label, confidence = ai_engine.analyze_sentiment(request.text)
        return pb.SentimentResponse(label=label, confidence=confidence)

    def GenerateText(self, request, context):
        self.authorize(context)
        self.validate(request.prompt, context)
        for token in ai_engine.generate_text(request.prompt):
            if not context.is_active():
                return
            yield pb.GenerateResponse(token=token)

    def bounded_stream(self, requests, field, context):
        total = 0
        for count, request in enumerate(requests, 1):
            if not context.is_active():
                return
            text = getattr(request, field)
            self.validate(text, context)
            total += len(text.encode("utf-8"))
            if count > MAX_STREAM_ITEMS or total > MAX_STREAM_BYTES:
                context.abort(
                    grpc.StatusCode.RESOURCE_EXHAUSTED,
                    "Stream exceeds the request limit.",
                )
            yield text

    def SummarizeBatch(self, request_iterator, context):
        self.authorize(context)
        chunks = list(self.bounded_stream(request_iterator, "text", context))
        if not chunks:
            context.abort(
                grpc.StatusCode.INVALID_ARGUMENT, "At least one chunk is required."
            )
        return pb.SummaryResponse(summary=ai_engine.summarize_text(" ".join(chunks)))

    def Chat(self, request_iterator, context):
        self.authorize(context)
        for message in self.bounded_stream(request_iterator, "message", context):
            yield pb.ChatMessage(
                user="AI Assistant", message=ai_engine.chat_response(message)
            )


def build_server(api_token=None):
    service = grpc.server(
        futures.ThreadPoolExecutor(max_workers=10),
        maximum_concurrent_rpcs=16,
        options=[("grpc.max_receive_message_length", 32_768)],
    )
    rpc.add_AIInferenceServicer_to_server(AIInferenceServicer(api_token), service)
    return service


def serve():
    address = f"{os.getenv('GRPC_HOST', '127.0.0.1')}:{os.getenv('PORT', '50051')}"
    service = build_server()
    if not service.add_insecure_port(address):
        raise RuntimeError("Could not bind gRPC listener.")
    service.start()
    print(f"gRPC listening on {address}")
    try:
        service.wait_for_termination()
    except KeyboardInterrupt:
        service.stop(5).wait()


if __name__ == "__main__":
    serve()
