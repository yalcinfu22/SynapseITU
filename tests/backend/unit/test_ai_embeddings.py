"""WBS-14.5: embedding client. All tests use the fake embedder or a mocked HTTP transport."""

import json
import math

import httpx
import pytest

from app.ai.config import AISettings
from app.ai.embeddings import QUERY_PREFIX, EmbeddingClient, OpenAICompatibleEmbeddingBackend
from app.ai.errors import AIProviderError, AIResponseError, AITimeoutError
from app.ai.testing import FakeEmbedder


def client(fake: FakeEmbedder, **kwargs) -> EmbeddingClient:
    return EmbeddingClient(fake, **({"dimensions": 1024, "timeout_s": 5} | kwargs))


def norm(v: list[float]) -> float:
    return math.sqrt(sum(x * x for x in v))


async def test_queries_get_the_instruction_prefix_and_documents_do_not():
    fake = FakeEmbedder()
    await client(fake).embed(["CV summary"], kind="query", feature="t")
    await client(fake).embed(["Opportunity"], kind="document", feature="t")
    assert fake.calls == [[QUERY_PREFIX + "CV summary"], ["Opportunity"]]


async def test_vectors_have_1024_dimensions_and_unit_length():
    vectors = await client(FakeEmbedder()).embed(["a", "b"], kind="document", feature="t")
    assert [len(v) for v in vectors] == [1024, 1024]
    assert all(abs(norm(v) - 1) < 1e-9 for v in vectors)


async def test_fake_embedder_is_deterministic():
    fake = FakeEmbedder()
    first = await client(fake).embed(["same", "other"], kind="document", feature="t")
    second = await client(fake).embed(["same"], kind="document", feature="t")
    assert first[0] == second[0]
    assert first[0] != first[1]


async def test_longer_vectors_are_cut_to_the_column_size():
    vectors = await client(FakeEmbedder(dimensions=2048)).embed(["a"], kind="document", feature="t")
    assert len(vectors[0]) == 1024
    assert abs(norm(vectors[0]) - 1) < 1e-9


async def test_shorter_vectors_are_rejected():
    with pytest.raises(AIResponseError):
        await client(FakeEmbedder(dimensions=512)).embed(["a"], kind="document", feature="t")


async def test_empty_input_makes_no_call():
    fake = FakeEmbedder()
    assert await client(fake).embed([], kind="document", feature="t") == []
    assert fake.calls == []


async def test_slow_embedding_raises_timeout():
    with pytest.raises(AITimeoutError):
        await client(FakeEmbedder(delay_s=1.0), timeout_s=0.05).embed(
            ["a"], kind="query", feature="t"
        )


async def test_usage_is_recorded():
    records = []
    await client(FakeEmbedder(), on_usage=records.append).embed(
        ["a", "b"], kind="document", feature="search"
    )
    [usage] = records
    assert (usage.feature, usage.kind, usage.model) == ("search", "embedding", "fake-embedder")
    assert usage.prompt_tokens > 0


# ---- OpenAI-compatible HTTP backend ------------------------------------------------------


def backend_with(handler, **env) -> OpenAICompatibleEmbeddingBackend:
    s = AISettings.from_env(
        {"EMBEDDING_BASE_URL": "http://emb.test/v1", "EMBEDDING_MODEL": "e"} | env
    )
    return OpenAICompatibleEmbeddingBackend(
        s, client=httpx.AsyncClient(transport=httpx.MockTransport(handler))
    )


async def test_http_backend_sends_an_openai_compatible_request_and_keeps_the_order():
    seen = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["url"] = str(request.url)
        seen["body"] = json.loads(request.content)
        data = [{"index": 1, "embedding": [0.0, 1.0]}, {"index": 0, "embedding": [1.0, 0.0]}]
        return httpx.Response(200, json={"data": data, "usage": {"prompt_tokens": 4}})

    batch = await backend_with(handler).embed(["first", "second"])
    assert seen["url"] == "http://emb.test/v1/embeddings"
    assert seen["body"] == {"model": "e", "input": ["first", "second"]}
    assert batch.vectors == [[1.0, 0.0], [0.0, 1.0]]
    assert batch.prompt_tokens == 4


async def test_http_backend_marks_server_errors_as_retryable():
    with pytest.raises(AIProviderError) as err:
        await backend_with(lambda request: httpx.Response(502)).embed(["a"])
    assert err.value.retryable is True


async def test_http_backend_turns_a_network_timeout_into_ai_timeout():
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectTimeout("slow", request=request)

    with pytest.raises(AITimeoutError):
        await backend_with(handler).embed(["a"])
