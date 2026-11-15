"""Embedding back-ends for the embedding-only baseline.

These are harness-local clients, not the platform's embedding client (that is the
WBS-14.5 AI services foundation). They exist so the baseline can run with the model chosen
in docs/adr/0002-embedding-model.md:

* ``openai`` – any OpenAI-compatible ``/v1/embeddings`` endpoint (DeepInfra, Ollama,
  vLLM, Hugging Face TEI).
* ``voyage`` – the Voyage AI embeddings API (``input_type`` query/document).
"""

import hashlib
import json
import math
import os
from collections.abc import Sequence
from pathlib import Path
from typing import Literal, Protocol

import httpx

Kind = Literal["query", "document"]
Vector = list[float]


class Embedder(Protocol):
    model: str

    async def embed(self, texts: Sequence[str], kind: Kind) -> list[Vector]: ...


def cosine(a: Sequence[float], b: Sequence[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b, strict=True))
    na, nb = math.sqrt(sum(x * x for x in a)), math.sqrt(sum(y * y for y in b))
    return 0.0 if na == 0 or nb == 0 else dot / (na * nb)


def _unit(v: Sequence[float]) -> Vector:
    n = math.sqrt(sum(x * x for x in v))
    return list(v) if n == 0 else [x / n for x in v]


class OpenAICompatibleEmbedder:
    def __init__(
        self,
        base_url: str,
        model: str,
        dimensions: int,
        api_key: str | None = None,
        query_prefix: str = "",
        document_prefix: str = "",
        batch_size: int = 64,
    ) -> None:
        self.model = f"{model}@{dimensions}"
        self._model, self._dims = model, dimensions
        self._url = base_url.rstrip("/") + "/embeddings"
        self._headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}
        self._prefix = {"query": query_prefix, "document": document_prefix}
        self._batch = batch_size

    async def embed(self, texts: Sequence[str], kind: Kind) -> list[Vector]:
        out: list[Vector] = []
        async with httpx.AsyncClient(timeout=60) as client:
            for i in range(0, len(texts), self._batch):
                chunk = [self._prefix[kind] + t for t in texts[i : i + self._batch]]
                resp = await client.post(
                    self._url, headers=self._headers, json={"model": self._model, "input": chunk}
                )
                resp.raise_for_status()
                data = sorted(resp.json()["data"], key=lambda d: d["index"])
                # Matryoshka truncation to the column size, then re-normalize.
                out += [_unit(d["embedding"][: self._dims]) for d in data]
        return out


class VoyageEmbedder:
    URL = "https://api.voyageai.com/v1/embeddings"

    def __init__(self, model: str, dimensions: int, api_key: str, batch_size: int = 64) -> None:
        self.model = f"{model}@{dimensions}"
        self._model, self._dims, self._key, self._batch = model, dimensions, api_key, batch_size

    async def embed(self, texts: Sequence[str], kind: Kind) -> list[Vector]:
        out: list[Vector] = []
        async with httpx.AsyncClient(timeout=60) as client:
            for i in range(0, len(texts), self._batch):
                resp = await client.post(
                    self.URL,
                    headers={"Authorization": f"Bearer {self._key}"},
                    json={
                        "model": self._model,
                        "input": list(texts[i : i + self._batch]),
                        "input_type": kind,
                        "output_dimension": self._dims,
                    },
                )
                resp.raise_for_status()
                out += [_unit(d["embedding"]) for d in resp.json()["data"]]
        return out


class DiskCache:
    """Caches vectors per (model, kind, text hash) so the labelled set is embedded once."""

    def __init__(self, inner: Embedder, path: Path | None) -> None:
        self.inner, self.model, self.path = inner, inner.model, path
        self.misses = 0
        self._cache: dict[str, Vector] = (
            json.loads(path.read_text(encoding="utf-8")) if path and path.exists() else {}
        )

    def _key(self, text: str, kind: Kind) -> str:
        return f"{self.model}|{kind}|{hashlib.sha256(text.encode()).hexdigest()}"

    async def embed(self, texts: Sequence[str], kind: Kind) -> list[Vector]:
        missing = [t for t in dict.fromkeys(texts) if self._key(t, kind) not in self._cache]
        if missing:
            self.misses += len(missing)
            for t, v in zip(missing, await self.inner.embed(missing, kind), strict=True):
                self._cache[self._key(t, kind)] = v
        return [self._cache[self._key(t, kind)] for t in texts]

    def save(self) -> None:
        if self.path:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self.path.write_text(json.dumps(self._cache), encoding="utf-8")


def from_env() -> Embedder:
    """Select the embedder from ``EVAL_EMBEDDER`` (openai | voyage) and friends."""
    backend = os.environ.get("EVAL_EMBEDDER")
    if not backend:
        raise SystemExit(
            "Set EVAL_EMBEDDER to 'openai' or 'voyage' (see docs/evaluation-harness.md)"
        )
    dims = int(os.environ.get("EVAL_EMBEDDING_DIMENSIONS", "1024"))
    model = os.environ["EVAL_EMBEDDING_MODEL"]
    key = os.environ.get("EVAL_EMBEDDING_API_KEY") or None
    if backend == "voyage":
        if not key:
            raise SystemExit("EVAL_EMBEDDING_API_KEY is required for the voyage backend")
        return VoyageEmbedder(model, dims, key)
    if backend == "openai":
        return OpenAICompatibleEmbedder(
            os.environ["EVAL_EMBEDDING_BASE_URL"],
            model,
            dims,
            key,
            query_prefix=os.environ.get("EVAL_QUERY_PREFIX", ""),
            document_prefix=os.environ.get("EVAL_DOCUMENT_PREFIX", ""),
        )
    raise SystemExit(f"unknown EVAL_EMBEDDER {backend!r}")
