"""Embedding client (WBS-14.5): every embedding of the platform goes through ``EmbeddingClient``.

    client = build_embedding_client()
    [cv_vector] = await client.embed([cv_summary], kind="query", feature="ai_search")
    vectors = await client.embed(opportunity_texts, kind="document", feature="ai_search")

Queries get the instruction prefix of ADR-0002; documents get none. The vectors are cut to the
column size (1024) and normalized to length 1.
"""

import asyncio
import math
import time
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Literal, Protocol

import httpx

from app.ai.config import AISettings
from app.ai.errors import AIResponseError, AITimeoutError
from app.ai.http import post_json
from app.ai.usage import Usage, UsageSink, log_usage

Kind = Literal["query", "document"]
Vector = list[float]

QUERY_PREFIX = (
    "Instruct: Given a student's CV summary, retrieve matching academic opportunities\nQuery: "
)


@dataclass(frozen=True)
class EmbeddingBatch:
    vectors: list[Vector]
    prompt_tokens: int


class EmbeddingBackend(Protocol):
    """``OpenAICompatibleEmbeddingBackend`` in the app, ``FakeEmbedder`` in tests."""

    model: str

    async def embed(self, texts: list[str]) -> EmbeddingBatch: ...


class EmbeddingClient:
    def __init__(
        self,
        backend: EmbeddingBackend,
        *,
        dimensions: int = 1024,
        timeout_s: float = 4,
        on_usage: UsageSink = log_usage,
    ) -> None:
        self.backend = backend
        self.dimensions = dimensions
        self.timeout_s = timeout_s
        self.on_usage = on_usage

    async def embed(self, texts: Sequence[str], *, kind: Kind, feature: str) -> list[Vector]:
        if not texts:
            return []
        prefix = QUERY_PREFIX if kind == "query" else ""
        start = time.perf_counter()
        batch: EmbeddingBatch | None = None
        try:
            async with asyncio.timeout(self.timeout_s):  # NFR-17
                batch = await self.backend.embed([prefix + t for t in texts])
            return [self._fit(v) for v in batch.vectors]
        except TimeoutError as err:
            raise AITimeoutError(f"embedding call took longer than {self.timeout_s} s") from err
        finally:
            self.on_usage(
                Usage(
                    feature=feature,
                    kind="embedding",
                    model=self.backend.model,
                    prompt_tokens=batch.prompt_tokens if batch else 0,
                    completion_tokens=0,
                    attempts=1,
                    seconds=time.perf_counter() - start,
                    ok=batch is not None,
                )
            )

    def _fit(self, vector: Vector) -> Vector:
        if len(vector) < self.dimensions:
            raise AIResponseError(
                f"the model returned {len(vector)} dimensions; the column needs {self.dimensions}"
            )
        cut = vector[: self.dimensions]
        length = math.sqrt(sum(x * x for x in cut))
        return cut if length == 0 else [x / length for x in cut]


class OpenAICompatibleEmbeddingBackend:
    """``POST {base_url}/embeddings``."""

    def __init__(self, settings: AISettings, client: httpx.AsyncClient | None = None) -> None:
        self.settings = settings
        self.model = settings.embedding_model
        self.client = client or httpx.AsyncClient()

    async def embed(self, texts: list[str]) -> EmbeddingBatch:
        s = self.settings
        url = s.embedding_base_url.rstrip("/") + "/embeddings"
        body = {"model": s.embedding_model, "input": texts}
        data = await post_json(self.client, url, s.embedding_api_key, body, s.embedding_timeout_s)
        try:
            items = sorted(data["data"], key=lambda d: d["index"])
            vectors = [item["embedding"] for item in items]
        except (KeyError, TypeError) as err:
            raise AIResponseError("the answer has no embeddings") from err
        if len(vectors) != len(texts):
            raise AIResponseError(f"sent {len(texts)} texts, received {len(vectors)} vectors")
        return EmbeddingBatch(vectors, (data.get("usage") or {}).get("prompt_tokens") or 0)
