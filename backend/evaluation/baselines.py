"""The two baselines the AI search must beat (WBS-15.4; NFR-26).

A *system* ranks a query's candidate documents. The AI search of WBS-8.2 will be added as a
third system with the same ``rank`` signature.
"""

import math
from collections import Counter
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Protocol

from app.text import tokenize
from evaluation.embedders import cosine


@dataclass(frozen=True)
class Doc:
    id: str
    text: str


class System(Protocol):
    name: str

    async def rank(self, query: str, candidates: Sequence[Doc]) -> list[str]: ...


class KeywordBaseline:
    """BM25 (k1=1.2, b=0.75) over folded, F5-stemmed terms. IDF is computed on the candidates."""

    name = "keyword"

    def __init__(self, k1: float = 1.2, b: float = 0.75) -> None:
        self.k1, self.b = k1, b

    async def rank(self, query: str, candidates: Sequence[Doc]) -> list[str]:
        tfs = {d.id: Counter(tokenize(d.text)) for d in candidates}
        lens = {i: sum(tf.values()) for i, tf in tfs.items()}
        n = len(candidates)
        avg = (sum(lens.values()) / n) if n else 0.0
        df = Counter(t for tf in tfs.values() for t in tf)
        terms = set(tokenize(query))

        def score(doc_id: str) -> float:
            tf, s = tfs[doc_id], 0.0
            for t in terms:
                if f := tf.get(t, 0):
                    idf = math.log(1 + (n - df[t] + 0.5) / (df[t] + 0.5))
                    s += (
                        idf
                        * f
                        * (self.k1 + 1)
                        / (f + self.k1 * (1 - self.b + self.b * lens[doc_id] / (avg or 1)))
                    )
            return s

        scores = {d.id: score(d.id) for d in candidates}
        return sorted(scores, key=lambda i: (-scores[i], i))


class EmbeddingBaseline:
    """Cosine similarity between the query and each candidate."""

    name = "embedding"

    def __init__(self, embedder) -> None:  # anything with embed(texts, kind)
        self.embedder = embedder

    async def rank(self, query: str, candidates: Sequence[Doc]) -> list[str]:
        if not candidates:
            return []
        q = (await self.embedder.embed([query], "query"))[0]
        vecs = await self.embedder.embed([d.text for d in candidates], "document")
        scores = {d.id: cosine(q, v) for d, v in zip(candidates, vecs, strict=True)}
        return sorted(scores, key=lambda i: (-scores[i], i))
