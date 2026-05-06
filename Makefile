install:
	pip install grpcio grpcio-tools protobuf

compile:
	python -m grpc_tools.protoc -I protos --python_out=. --grpc_python_out=. protos/ai_inference.proto

server:
	python server/server.py

client:
	python client/client.py

docker-build:
	docker build -t ai-grpc-server .

compose-up:
	docker compose up --build

compose-down:
	docker compose down