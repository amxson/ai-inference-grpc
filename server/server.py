import sys
import os
import time
from concurrent import futures

import grpc

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import ai_inference_pb2
import ai_inference_pb2_grpc

from ai_engine import (
    analyze_sentiment,
    generate_text,
    summarize_text,
    chat_response,
)


class AIInferenceServicer(ai_inference_pb2_grpc.AIInferenceServicer):

    def AnalyzeSentiment(self, request, context):
        label, confidence = analyze_sentiment(request.text)

        return ai_inference_pb2.SentimentResponse(
            label=label,
            confidence=confidence
        )

    def GenerateText(self, request, context):
        for token in generate_text(request.prompt):
            yield ai_inference_pb2.GenerateResponse(token=token)

    def SummarizeBatch(self, request_iterator, context):
        chunks = []

        for chunk in request_iterator:
            chunks.append(chunk.text)

        full_text = " ".join(chunks)
        summary = summarize_text(full_text)

        return ai_inference_pb2.SummaryResponse(summary=summary)

    def Chat(self, request_iterator, context):
        for message in request_iterator:
            response = chat_response(message.message)

            yield ai_inference_pb2.ChatMessage(
                user="AI Assistant",
                message=response
            )


def serve():
    port = os.getenv("PORT", "50051")

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

    ai_inference_pb2_grpc.add_AIInferenceServicer_to_server(
        AIInferenceServicer(),
        server
    )

    server.add_insecure_port(f"[::]:{port}")
    server.start()

    print(f"AI Inference gRPC server started on port {port}")

    try:
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        print("Stopping server...")
        server.stop(0)


if __name__ == "__main__":
    serve()