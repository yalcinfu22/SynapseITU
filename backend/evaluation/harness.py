"""Matching evaluation harness (WBS-15.4: baselines and metrics).

Runs the keyword-only and embedding-only baselines over a labelled relevance set and
reports precision@5 (the D-04 / NFR-26 metric) and MRR@10. The AI search (WBS-8.2) is
added later as a third system and must beat both baselines.

Labelled set format (JSON) — see docs/evaluation-harness.md::

    {"documents": [{"id": "...", "text": "..."}],
     "queries":   [{"id": "...", "text": "<CV summary>",
                    "candidates": ["doc ids: the student's eligible pool"],   # optional
                    "relevant":   ["doc ids"]}]}

Usage (settings as in backend/.env.example)::

    uv run python -m evaluation.harness --data path/to/labelled_set.json --out report.json
"""

import argparse
import asyncio
import json
from pathlib import Path

from app.ai import build_embedding_client
from evaluation.baselines import Doc, EmbeddingBaseline, KeywordBaseline, System
from evaluation.embedders import DiskCache
from evaluation.metrics import mean, mrr_at_k, precision_at_k

HERE = Path(__file__).parent


def load(path: Path) -> tuple[dict[str, Doc], list[dict]]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    docs = {d["id"]: Doc(d["id"], d["text"]) for d in raw["documents"]}
    for q in raw["queries"]:
        unknown = (set(q.get("candidates", [])) | set(q["relevant"])) - docs.keys()
        if unknown:
            raise ValueError(f"query {q['id']} references unknown documents: {sorted(unknown)}")
    return docs, raw["queries"]


async def evaluate(
    docs: dict[str, Doc], queries: list[dict], systems: list[System], k: int = 5
) -> dict:
    per_query: dict[str, dict[str, dict[str, float]]] = {}
    for q in queries:
        cand_ids = q.get("candidates") or list(docs)
        candidates = [docs[i] for i in cand_ids]
        relevant = set(q["relevant"])
        per_query[q["id"]] = {}
        for system in systems:
            ranked = await system.rank(q["text"], candidates)
            per_query[q["id"]][system.name] = {
                f"precision@{k}": precision_at_k(ranked, relevant, set(cand_ids), k),
                "mrr@10": mrr_at_k(ranked, relevant),
            }
    summary = {
        s.name: {
            m: round(mean([r[s.name][m] for r in per_query.values()]), 4)
            for m in (f"precision@{k}", "mrr@10")
        }
        for s in systems
    }
    return {
        "queries": len(queries),
        "documents": len(docs),
        "summary": summary,
        "per_query": per_query,
    }


def to_markdown(report: dict) -> str:
    lines = [
        f"### Matching baselines — {report['queries']} queries, {report['documents']} documents",
        f"Embedding model: `{report['embedding_model']}`",
        "",
        "| System | precision@5 | MRR@10 |",
        "|---|---|---|",
    ]
    lines += [
        f"| {s} | {m['precision@5']:.3f} | {m['mrr@10']:.3f} |"
        for s, m in report["summary"].items()
    ]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the WBS-15.4 matching baselines.")
    parser.add_argument("--data", type=Path, required=True, help="labelled set (JSON)")
    parser.add_argument("--cache", type=Path, default=HERE / ".cache" / "embeddings.json")
    parser.add_argument("--out", type=Path, help="write the JSON report here")
    args = parser.parse_args(argv)

    embedder = DiskCache(build_embedding_client(), args.cache)
    docs, queries = load(args.data)
    report = asyncio.run(evaluate(docs, queries, [KeywordBaseline(), EmbeddingBaseline(embedder)]))
    embedder.save()
    report["embedding_model"] = embedder.model
    report["embedding_cache_misses"] = embedder.misses
    print(to_markdown(report))
    if args.out:
        args.out.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
