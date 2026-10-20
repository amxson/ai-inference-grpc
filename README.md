# AI Inference over gRPC

A Python service demonstrating the four gRPC call patterns against one inference adapter. Gemini is optional: without a key, deterministic local responses let you run the client and tests without network access.

| RPC | Pattern | Behavior |
| --- | --- | --- |
| `AnalyzeSentiment` | Unary | Label and confidence for one text |
| `GenerateText` | Server streaming | An answer emitted as word chunks |
| `SummarizeBatch` | Client streaming | Bounded text chunks combined into one summary |
| `Chat` | Bidirectional streaming | One response per incoming message |

The provider adapter currently generates a complete response before emitting word chunks. This demonstrates gRPC streaming, not native Gemini token streaming. Chat handles each message independently; it does not retain conversation memory.

## Run locally

Use Python 3.11 or newer, from the repository root:

```sh
python -m venv .venv
# Linux/macOS: source .venv/bin/activate
# PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
python -m server.server
```

In another terminal, with the same environment active:

```sh
python client/client.py
python -m pytest -q
```

Set `GEMINI_API_KEY` in the server environment to enable Gemini. `GEMINI_MODEL` defaults to `gemini-2.5-flash`; choose a model available to your account. Provider calls have a ten-second HTTP timeout and fall back locally on failure. The client has explicit RPC deadlines. Never commit provider credentials.

## Limits and access

The listener defaults to `127.0.0.1:50051`. `GRPC_HOST` and `PORT` override the bind address. Each text is limited to 16 KiB of UTF-8; a stream accepts at most 64 items and 64 KiB total. Blank text returns `INVALID_ARGUMENT`, oversized requests return `RESOURCE_EXHAUSTED`, and the service accepts at most 16 concurrent RPCs.

Set the same `GRPC_API_TOKEN` on server and client to require bearer metadata on every RPC. A missing or incorrect token returns `UNAUTHENTICATED`. The built-in transport is plaintext for local development: keep it on loopback or a private network. Public hosting requires TLS termination, authentication, and deployment-level rate limits; a bearer token alone does not encrypt traffic.

## Containers

```sh
docker compose up --build
python client/client.py
docker compose down
```

Compose starts three backend processes and an Nginx HTTP/2 proxy. Only the proxy is published, on localhost port 50051. Set provider/token variables in your shell or an untracked `.env` file before starting Compose. Each backend receives the same settings. The application image runs as an unprivileged user and excludes local credentials.

For a standalone image:

```sh
docker build -f server/Dockerfile -t ai-grpc-server .
```

Docker must be installed and running; unit and RPC tests do not require it.

## Contract and layout

`protos/ai_inference.proto` defines the contract. Regenerate the checked-in bindings after changing it:

```sh
make compile
```

`server/server.py` handles validation, access, and RPC lifecycles; `server/ai_engine.py` handles inference and fallback behavior. `client/client.py` exercises every call pattern. `tests/test_service.py` starts an ephemeral local server and checks the wire-level responses, authentication, and request limits.

Author: Amar Asfaw.
