# Use official Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements
COPY server/requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project files
COPY server/ server/
COPY ai_inference_pb2.py ai_inference_pb2_grpc.py ./
RUN useradd --create-home appuser
USER appuser

# Expose gRPC port
EXPOSE 50051

# Run server
CMD ["python", "-m", "server.server"]
