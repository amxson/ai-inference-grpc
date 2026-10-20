from concurrent.futures import ThreadPoolExecutor
from unittest.mock import patch

import grpc
import pytest
import ai_inference_pb2 as pb
import ai_inference_pb2_grpc as rpc
from server.server import build_server, MAX_TEXT_BYTES, MAX_STREAM_ITEMS
from server import ai_engine


@pytest.fixture
def service():
    server = build_server(api_token="test-token")
    port = server.add_insecure_port("127.0.0.1:0")
    server.start()
    with grpc.insecure_channel(f"127.0.0.1:{port}") as channel:
        yield rpc.AIInferenceStub(channel)
    server.stop(0).wait()


AUTH = (("authorization", "Bearer test-token"),)


def test_all_four_rpc_shapes(service):
    with patch.object(ai_engine, "call_gemini", return_value=""), patch.object(
        ai_engine.time, "sleep"
    ):
        assert (
            service.AnalyzeSentiment(
                pb.SentimentRequest(text="great"), metadata=AUTH, timeout=5
            ).label
            == "POSITIVE"
        )
        assert list(
            service.GenerateText(
                pb.GenerateRequest(prompt="hello"), metadata=AUTH, timeout=5
            )
        )
        assert (
            service.SummarizeBatch(
                iter([pb.TextChunk(text="hello world")]), metadata=AUTH, timeout=5
            ).summary
            == "hello world"
        )
        messages = list(
            service.Chat(
                iter([pb.ChatMessage(message="hello")]), metadata=AUTH, timeout=5
            )
        )
        assert len(messages) == 1 and "hello" in messages[0].message


@pytest.mark.parametrize("shape", ["unary", "output", "input", "duplex"])
def test_every_rpc_requires_authentication(service, shape):
    with pytest.raises(grpc.RpcError) as error:
        if shape == "unary":
            service.AnalyzeSentiment(pb.SentimentRequest(text="great"), timeout=5)
        elif shape == "output":
            list(service.GenerateText(pb.GenerateRequest(prompt="hello"), timeout=5))
        elif shape == "input":
            service.SummarizeBatch(iter([pb.TextChunk(text="hello")]), timeout=5)
        else:
            list(service.Chat(iter([pb.ChatMessage(message="hello")]), timeout=5))
    assert error.value.code() == grpc.StatusCode.UNAUTHENTICATED


@pytest.mark.parametrize(
    "text,code",
    [
        ("  ", grpc.StatusCode.INVALID_ARGUMENT),
        ("a" * (MAX_TEXT_BYTES + 1), grpc.StatusCode.RESOURCE_EXHAUSTED),
    ],
)
def test_invalid_inputs_do_not_reach_provider(service, text, code):
    with patch.object(ai_engine, "analyze_sentiment") as provider, pytest.raises(
        grpc.RpcError
    ) as error:
        service.AnalyzeSentiment(
            pb.SentimentRequest(text=text), metadata=AUTH, timeout=5
        )
    assert error.value.code() == code
    provider.assert_not_called()


def test_batch_is_bounded_before_provider_call(service):
    with patch.object(ai_engine, "summarize_text") as provider, pytest.raises(
        grpc.RpcError
    ) as error:
        service.SummarizeBatch(
            (pb.TextChunk(text="x") for _ in range(MAX_STREAM_ITEMS + 1)),
            metadata=AUTH,
            timeout=5,
        )
    assert error.value.code() == grpc.StatusCode.RESOURCE_EXHAUSTED
    provider.assert_not_called()


def test_empty_batch_is_invalid(service):
    with pytest.raises(grpc.RpcError) as error:
        service.SummarizeBatch(iter([]), metadata=AUTH, timeout=5)
    assert error.value.code() == grpc.StatusCode.INVALID_ARGUMENT


@pytest.mark.parametrize(
    "reply", ["POSITIVE,nan", "NEGATIVE,1.5", "FAKE,0.9", "malformed"]
)
def test_invalid_provider_sentiment_uses_fallback(reply):
    with patch.object(ai_engine, "call_gemini", return_value=reply):
        label, confidence = ai_engine.analyze_sentiment("a normal day")
    assert label == "NEUTRAL" and 0 <= confidence <= 1
