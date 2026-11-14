"""Tests for the WBS-15.4 matching evaluation harness (baselines and metrics)."""

import json
import math
from pathlib import Path

import pytest

from evaluation.baselines import Doc, EmbeddingBaseline, KeywordBaseline
from evaluation.embedders import DiskCache
from evaluation.harness import evaluate, load
from evaluation.metrics import mrr_at_k, precision_at_k
from evaluation.text import fold, tokenize


class StubEmbedder:
    """Test stub: one dimension per word in VOCAB; counts calls to the model."""

    VOCAB = ["economics", "survey", "vision", "image"]

    def __init__(self) -> None:
        self.model = "stub"
        self.calls = 0

    async def embed(self, texts, kind):
        self.calls += 1
        return [[float(w in t.lower()) for w in self.VOCAB] for t in texts]


DOCS = [
    Doc("cv", "Bilgisayarlı görü ve görüntü işleme laboratuvarı, vision lab"),
    Doc("econ", "Behavioural economics survey"),
]


def test_turkish_folding_and_f5_stemming():
    assert fold("GÖRÜNTÜ İŞLEME ılık") == "goruntu isleme ilik"
    assert tokenize("goruntu isleme") == tokenize("Görüntü İşlemede")


def test_precision_at_5_divides_by_reachable_relevant_items():
    cands = set("abcdefgh")
    assert precision_at_k(list("axbyz"), {"a", "b"}, cands) == 1.0
    assert precision_at_k(list("abxyz"), set("abcdefg"), cands) == pytest.approx(0.4)
    assert math.isnan(precision_at_k(list("ab"), {"q"}, cands))  # no relevant candidate


def test_mrr():
    assert mrr_at_k(list("xya"), {"a"}) == pytest.approx(1 / 3)
    assert mrr_at_k(list("xyz"), {"a"}) == 0.0


async def test_keyword_baseline_matches_ascii_query_to_turkish_text():
    assert (await KeywordBaseline().rank("goruntu isleme", DOCS))[0] == "cv"


async def test_embedding_baseline_ranks_by_similarity():
    ranked = await EmbeddingBaseline(StubEmbedder()).rank("economics survey", DOCS)
    assert ranked == ["econ", "cv"]


async def test_disk_cache_sends_each_text_to_the_model_once(tmp_path: Path):
    stub = StubEmbedder()
    cache = DiskCache(stub, tmp_path / "c.json")
    await cache.embed(["vision", "vision"], "query")
    cache.save()
    again = DiskCache(stub, tmp_path / "c.json")
    await again.embed(["vision"], "query")
    assert stub.calls == 1


async def test_only_candidates_count(tmp_path: Path):
    data = {
        "documents": [{"id": "a", "text": "robot"}, {"id": "b", "text": "robot robot"}],
        "queries": [{"id": "q", "text": "robot", "candidates": ["a"], "relevant": ["a", "b"]}],
    }
    path = tmp_path / "set.json"
    path.write_text(json.dumps(data))
    docs, queries = load(path)
    report = await evaluate(docs, queries, [KeywordBaseline()])
    assert report["summary"]["keyword"]["precision@5"] == 1.0  # "b" is not a candidate


def test_unknown_document_ids_are_rejected(tmp_path: Path):
    path = tmp_path / "bad.json"
    path.write_text(
        json.dumps({"documents": [], "queries": [{"id": "q", "text": "t", "relevant": ["zz"]}]})
    )
    with pytest.raises(ValueError, match="unknown documents"):
        load(path)
