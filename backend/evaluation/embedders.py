"""Embeddings for the embedding-only baseline.

The harness uses the platform's embedding client (``app.ai``, WBS-14.5), so the baseline
uses the same model and settings as the product (ADR-0002). This module only adds a disk
cache, so that the labelled set is embedded once.
"""

import hashlib
import json
import math
from collections.abc import Sequence
from pathlib import Path

from app.ai import EmbeddingClient
from app.ai.embeddings import Kind

Vector = list[float]


def cosine(a: Sequence[float], b: Sequence[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b, strict=True))
    na, nb = math.sqrt(sum(x * x for x in a)), math.sqrt(sum(y * y for y in b))
    return 0.0 if na == 0 or nb == 0 else dot / (na * nb)


class DiskCache:
    """Caches vectors per (model, kind, text hash) on disk."""

    def __init__(self, client: EmbeddingClient, path: Path | None) -> None:
        self.client, self.path = client, path
        self.model = client.backend.model
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
            vectors = await self.client.embed(missing, kind=kind, feature="evaluation")
            for t, v in zip(missing, vectors, strict=True):
                self._cache[self._key(t, kind)] = v
        return [self._cache[self._key(t, kind)] for t in texts]

    def save(self) -> None:
        if self.path:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self.path.write_text(json.dumps(self._cache), encoding="utf-8")
