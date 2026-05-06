# AI Inference Microservice using gRPC

This project implements an AI Inference Microservice using **gRPC**, **Protocol Buffers**, **Python**, **Docker**, **Docker Compose**, and **Nginx Layer 7 Load Balancing**.

The system demonstrates all four gRPC communication models:

1. Unary RPC - Sentiment Analysis
2. Server Streaming RPC - Real-time text generation
3. Client Streaming RPC - Batch summarization
4. Bidirectional Streaming RPC - Live chat assistant

---

## Architecture

```text
Client CLI
   |
   v
Nginx gRPC Load Balancer
   |
   +--> AI Server 1
   +--> AI Server 2
   +--> AI Server 3

The client connects to the Nginx load balancer, not directly to the backend servers.

Project Structure
ai-inference-grpc/
├── protos/
│   └── ai_inference.proto
├── server/
│   ├── server.py
│   ├── ai_engine.py
│   ├── requirements.txt
│   └── Dockerfile
├── client/
│   ├── client.py
│   └── requirements.txt
├── nginx/
│   └── nginx.conf
├── screenshots/
├── docker-compose.yml
├── Makefile
└── README.md
gRPC API

The service is defined in:

protos/ai_inference.proto

It contains four RPC methods:

RPC Method	Type	Purpose
AnalyzeSentiment	Unary	Sends one text and receives sentiment label + confidence
GenerateText	Server Streaming	Sends one prompt and receives generated tokens one by one
SummarizeBatch	Client Streaming	Sends multiple text chunks and receives one summary
Chat	Bidirectional Streaming	Sends and receives chat messages over one connection
Local Setup

Install dependencies:

pip install grpcio grpcio-tools protobuf

Compile protobuf:

python -m grpc_tools.protoc -I protos --python_out=. --grpc_python_out=. protos/ai_inference.proto

Run the server:

python server/server.py

In another terminal, run the client:

python client/client.py
Docker Setup

Build the Docker image:

docker build -t ai-grpc-server .

Run the full system with 3 backend servers and Nginx load balancer:

docker compose up --build

Run the client through Nginx:

python client/client.py

Stop containers:

docker compose down

Note: Docker configuration is included for the required containerized deployment.
The gRPC server and client were tested locally using Python. Docker testing depends on having Docker Desktop/WSL running correctly.

Makefile Commands
make install
make compile
make server
make client
make docker-build
make compose-up
make compose-down
Example Output
Connecting to gRPC server at localhost:50051

=== Unary RPC: Sentiment Analysis ===
Label: POSITIVE
Confidence: 0.95

=== Server Streaming RPC: Text Generation ===
Generated text: This is a simulated AI response for your prompt: Explain gRPC in simple words

=== Client Streaming RPC: Batch Summarization ===
Sending chunk: gRPC is a modern RPC framework.
Sending chunk: It uses Protocol Buffers for strict contracts.
Sending chunk: It supports unary, server streaming, client streaming, and bidirectional streaming.
Sending chunk: It is useful for scalable microservices and low latency systems.
Summary: gRPC is a modern RPC framework. It uses Protocol Buffers for strict contracts. It supports unary, server streaming, client streaming,...

=== Bidirectional Streaming RPC: Live Chat ===
Client: Hello AI assistant
AI Assistant: AI Assistant received your message: Hello AI assistant
Client: What is gRPC?
AI Assistant: AI Assistant received your message: What is gRPC?
Client: Why is streaming useful?
AI Assistant: AI Assistant received your message: Why is streaming useful?



Why gRPC?

gRPC is useful for this project because:

It uses Protocol Buffers for a strict API contract.
It supports all four communication models.
It is efficient for microservices.
It supports streaming, which is important for AI/LLM responses.
It runs on HTTP/2, making it suitable for low-latency systems.
AI Backend

This implementation currently uses a mock AI engine in:

server/ai_engine.py

The mock engine simulates:

Sentiment analysis
Token-by-token text generation
Text summarization
Chat response

It can later be replaced with real AI APIs such as Gemini, Groq, or Ollama.

Load Balancing

Nginx is configured as a gRPC Layer 7 load balancer in:

nginx/nginx.conf

It distributes traffic across three backend gRPC servers:

ai-server-1
ai-server-2
ai-server-3
Author

Name: Amar Asfaw
Group: G-10
Project: AI Inference Microservice using gRPC