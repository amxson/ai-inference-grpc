install:
	python -m pip install -r requirements-dev.txt

compile:
	python -m grpc_tools.protoc -I protos --python_out=. --grpc_python_out=. protos/ai_inference.proto

server:
	python -m server.server

client:
	python client/client.py

docker-build:
	docker build -f server/Dockerfile -t ai-grpc-server .

compose-up:
	docker compose up --build

compose-down:
	docker compose down

test:
	python -m pytest -q
