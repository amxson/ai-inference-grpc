import sys
import os
import time

import grpc

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import ai_inference_pb2
import ai_inference_pb2_grpc


def run_unary(stub):
    print("\n=== Unary RPC: Sentiment Analysis ===")

    request = ai_inference_pb2.SentimentRequest(
        text="I love this product. It is amazing!"
    )

    response = stub.AnalyzeSentiment(request)

    print(f"Label: {response.label}")
    print(f"Confidence: {response.confidence:.2f}")


def run_server_streaming(stub):
    print("\n=== Server Streaming RPC: Text Generation ===")

    request = ai_inference_pb2.GenerateRequest(
        prompt="Explain gRPC in simple words"
    )

    print("Generated text: ", end="")

    for response in stub.GenerateText(request):
        print(response.token, end="", flush=True)

    print()


def generate_chunks():
    chunks = [
        "gRPC is a modern RPC framework.",
        "It uses Protocol Buffers for strict contracts.",
        "It supports unary, server streaming, client streaming, and bidirectional streaming.",
        "It is useful for scalable microservices and low latency systems."
    ]

    for chunk in chunks:
        print(f"Sending chunk: {chunk}")
        yield ai_inference_pb2.TextChunk(text=chunk)
        time.sleep(0.2)


def run_client_streaming(stub):
    print("\n=== Client Streaming RPC: Batch Summarization ===")

    response = stub.SummarizeBatch(generate_chunks())

    print(f"Summary: {response.summary}")


def chat_messages():
    messages = [
        "Hello AI assistant",
        "What is gRPC?",
        "Why is streaming useful?"
    ]

    for msg in messages:
        print(f"Client: {msg}")
        yield ai_inference_pb2.ChatMessage(
            user="Client",
            message=msg
        )
        time.sleep(0.3)


def run_bidirectional_streaming(stub):
    print("\n=== Bidirectional Streaming RPC: Live Chat ===")

    responses = stub.Chat(chat_messages())

    for response in responses:
        print(f"{response.user}: {response.message}")


def main():
    target = os.getenv("GRPC_TARGET", "localhost:50051")

    print(f"Connecting to gRPC server at {target}")

    with grpc.insecure_channel(target) as channel:
        stub = ai_inference_pb2_grpc.AIInferenceStub(channel)

        run_unary(stub)
        run_server_streaming(stub)
        run_client_streaming(stub)
        run_bidirectional_streaming(stub)


if __name__ == "__main__":
    main()