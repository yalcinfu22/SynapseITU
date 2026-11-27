# Matching evaluation harness (WBS-15.4)

The harness measures two simple search methods. The AI search (WBS-8.2) must get a better score than both (D-04, NFR-26).

| Part of WBS-15.4 | Owner | Status |
|---|---|---|
| Baselines and metrics (code in `backend/evaluation/`) | Furkan | Done |
| Labelled set and the CI job | Amr | Not started |

## What it measures

| Method | How it ranks the opportunities |
|---|---|
| **Keyword** | It counts the shared words (BM25). It removes Turkish letters and cuts each word to 5 letters, so "görüntü işlemede" matches "goruntu isleme". |
| **Embedding** | It compares meanings with the embedding model (ADR-0002). |

Terms:

- **Baseline**: a simple method that a better method must beat.
- **precision@5**: the share of correct opportunities in the first 5 results. Example: 3 correct in the first 5 gives 0.6. If a student has fewer than 5 correct opportunities, we divide by that number. Thus a perfect list always gets 1.0.
- **MRR@10**: 1 divided by the position of the first correct result. Example: the first correct result is at position 2, so the value is 0.5. We use it only to find problems.
- **Candidates**: the opportunities that the student can apply to (the eligible pool). The harness ranks only these, because the AI search shows only these.

## Labelled set format

The labelled set is a JSON file:

```json
{
  "documents": [{"id": "opp-1", "text": "title, description and requirements"}],
  "queries": [
    {
      "id": "student-1",
      "text": "CV summary: skills and interests",
      "candidates": ["opp-1", "opp-2"],
      "relevant": ["opp-1"]
    }
  ]
}
```

- `relevant` contains the correct opportunities for the student. Write them before you run the harness. Do not change them after you see the results.
- If you do not give `candidates`, the harness uses all documents.
- If an id in `candidates` or `relevant` is not in `documents`, the harness stops with an error.

## How to run it

Run the command in `backend/`. The harness uses the embedding client of the product (`app.ai`), so it reads the same settings: `EMBEDDING_BASE_URL`, `EMBEDDING_MODEL` and `EMBEDDING_API_KEY` (see `backend/.env.example`). The defaults use Ollama on your computer.

```bash
uv run --locked python -m evaluation.harness --data <labelled_set.json> --out report.json
```

- The harness keeps the embeddings in `backend/evaluation/.cache/`. It does not send the same text twice. Git ignores this folder.
- For CI: keep this folder with `actions/cache`. Use the hash of the labelled set as the key.
