# AI Inference Microservice using gRPC

This project implements an **AI Inference Microservice** using **gRPC**, **Protocol Buffers**, **Python**, **Gemini API**, **Docker**, **Docker Compose**, and **Nginx Layer 7 Load Balancing**.

The system demonstrates all four gRPC communication models:

1. Unary RPC - Sentiment Analysis
2. Server Streaming RPC - Real-time text generation
3. Client Streaming RPC - Batch summarization
4. Bidirectional Streaming RPC - Live chat assistant

---

## Project Idea

The goal of this project is to build a backend AI microservice that receives requests from a client, sends the input to an AI backend, and returns the AI result using gRPC.

The AI backend is implemented using **Gemini API**. If Gemini is not configured, the system can fall back to mock responses for local testing.

---

## Architecture

```text
Client CLI
   |
   v
gRPC Server
   |
   v
Gemini API
   |
   v
gRPC Response

For containerized deployment, the intended architecture is:

Client CLI
   |
   v
Nginx gRPC Load Balancer
   |
   +--> AI Server 1
   +--> AI Server 2
   +--> AI Server 3
          |
          v
       Gemini API

The client connects to the gRPC service. In the Docker deployment design, the client connects to the Nginx load balancer, and Nginx forwards requests to one of the backend gRPC servers.

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
├── README.md
├── ai_inference_pb2.py
└── ai_inference_pb2_grpc.py
gRPC API

The service contract is defined in:

protos/ai_inference.proto

The .proto file defines one service called AIInference with four RPC methods:

RPC Method	Type	Purpose
AnalyzeSentiment	Unary RPC	Sends one text and receives a sentiment label plus confidence score
GenerateText	Server Streaming RPC	Sends one prompt and receives generated tokens one by one
SummarizeBatch	Client Streaming RPC	Sends multiple text chunks and receives one final summary
Chat	Bidirectional Streaming RPC	Sends and receives chat messages through one open stream
Why gRPC?

gRPC is useful for this project because:

It uses Protocol Buffers for a strict API contract.
It supports all four RPC communication models.
It is efficient for microservice communication.
It supports streaming, which is important for AI-generated responses.
It runs on HTTP/2, making it suitable for low-latency systems.
Protocol Buffers

Protocol Buffers are used to define the request and response messages.

After compiling the .proto file, these generated files are created:

ai_inference_pb2.py
ai_inference_pb2_grpc.py

ai_inference_pb2.py contains the generated message classes.

ai_inference_pb2_grpc.py contains the generated gRPC client and server classes, such as the stub and servicer.

These files are generated automatically and should not be edited manually.

AI Backend

The AI backend logic is located in:

server/ai_engine.py

This file is responsible for calling Gemini API and handling AI-related tasks.

It includes functions for:

Sentiment analysis
Text generation
Batch summarization
Chat response

The gRPC networking logic is kept separate in:

server/server.py

This separation makes the project easier to maintain because the AI provider can be changed later without changing the gRPC contract.

For example, Gemini could later be replaced with Groq, Ollama, or another AI backend.

Gemini API Setup

This project uses Gemini API through the google-genai package.

Install dependencies:

pip install -r server/requirements.txt

Set your Gemini API key as an environment variable.

Windows PowerShell
$env:GEMINI_API_KEY="YOUR_GEMINI_API_KEY"
macOS/Linux
export GEMINI_API_KEY="YOUR_GEMINI_API_KEY"

Then start the server from the same terminal where the environment variable is set:

python server/server.py

Important:

Do not put your Gemini API key inside the source code, README, screenshots, or GitHub repository.

Local Setup

Install dependencies:

pip install grpcio grpcio-tools protobuf google-genai

Or install from the server requirements file:

pip install -r server/requirements.txt

Compile protobuf:

python -m grpc_tools.protoc -I protos --python_out=. --grpc_python_out=. protos/ai_inference.proto

Start the server:

python server/server.py

In another terminal, run the client:

python client/client.py
Running with Gemini

In the server terminal:

$env:GEMINI_API_KEY="YOUR_GEMINI_API_KEY"
python server/server.py

In another terminal:

python client/client.py

If Gemini is configured correctly, the responses will come from Gemini instead of the mock fallback.

Docker Setup

Build the Docker image:

docker build -t ai-grpc-server .

Run the full system with three backend servers and Nginx load balancer:

docker compose up --build

Run the client through Nginx:

python client/client.py

Stop containers:

docker compose down

Note: Docker configuration is included for the required containerized deployment.
The gRPC server and client were tested locally using Python and Gemini API. Docker testing depends on having Docker Desktop/WSL running correctly.

Docker Compose Architecture

The docker-compose.yml file defines:

ai-server-1
ai-server-2
ai-server-3
nginx

Each backend server runs the same gRPC AI service.

Nginx acts as a gRPC load balancer and distributes incoming requests across the backend servers.

Nginx Load Balancing

Nginx is configured in:

nginx/nginx.conf

It listens for gRPC traffic using HTTP/2 and forwards requests to the backend servers using:

grpc_pass grpc://ai_backend;

The backend server group contains:

ai-server-1:50051
ai-server-2:50051
ai-server-3:50051

This design improves scalability and avoids relying on only one backend server.

Makefile Commands
make install
make compile
make server
make client
make docker-build
make compose-up
make compose-down
Example Output with Gemini
Connecting to gRPC server at localhost:50051

=== Unary RPC: Sentiment Analysis ===
Label: POSITIVE
Confidence: 0.99

=== Server Streaming RPC: Text Generation ===
Generated text: gRPC is a modern way for different computer programs to communicate with each other...

=== Client Streaming RPC: Batch Summarization ===
Sending chunk: gRPC is a modern RPC framework.
Sending chunk: It uses Protocol Buffers for strict contracts.
Sending chunk: It supports unary, server streaming, client streaming, and bidirectional streaming.
Sending chunk: It is useful for scalable microservices and low latency systems.
Summary: gRPC is a modern RPC framework that utilizes Protocol Buffers for strict contracts. It supports four types of streaming and is ideal for scalable microservices and low-latency systems.

=== Bidirectional Streaming RPC: Live Chat ===
Client: Hello AI assistant
Client: What is gRPC?
Client: Why is streaming useful?
AI Assistant: Hello!
AI Assistant: gRPC is an open-source, high-performance Remote Procedure Call framework developed by Google...
AI Assistant: Streaming allows data to be sent gradually instead of waiting for the full response.


The Gemini API key is loaded from an environment variable:

GEMINI_API_KEY

The API key should never be committed to GitHub.

Recommended .gitignore entries:

__pycache__/
*.pyc
.venv/
.env
Author

Name: Amar Asfaw
Group: G-10
Project: AI Inference Microservice using gRPC