"""WBS-14.1 spike (issue #25): one schema-validated LLM call and one embedding call.

This is a throwaway check, not the platform's AI client (that is WBS-14.5). It talks to any
OpenAI-compatible server, so the same script runs against a local Ollama or a hosted provider.
The defaults are the local Ollama models; change the provider with environment variables:

    LLM_BASE_URL          default http://localhost:11434/v1
    LLM_MODEL             default qwen3.5:4b-q4_K_M
    LLM_API_KEY           default empty (Ollama needs none)
    LLM_REASONING_EFFORT  default "none" (turns off Qwen thinking); set it empty to omit it
    EMBEDDING_BASE_URL    default LLM_BASE_URL
    EMBEDDING_MODEL       default qwen3-embedding:0.6b
    EMBEDDING_API_KEY     default LLM_API_KEY

Run from backend/:  uv run --locked python spikes/ai_spike.py
The CV and the opportunities below are made up. Never put real CVs or API keys in this file.
"""

import math
import os
import re
import sys
import time

import httpx
from pydantic import BaseModel, ValidationError

CV_TEXT = (
    "Bilgisayar mühendisliği 3. sınıf öğrencisiyim. Python, FastAPI ve PostgreSQL ile "
    "projeler yaptım. Pandas ile veri analizi yaptım. Doğal dil işleme ve öneri sistemleri "
    "ile ilgileniyorum."
)

OPPORTUNITIES = {
    "nlp-lab": "Doğal dil işleme laboratuvarında Türkçe metinler üzerinde araştırma stajı.",
    "ml-intern": "Machine learning internship: build recommendation models in Python.",
    "web-backend": "Backend developer intern: REST APIs with FastAPI and PostgreSQL.",
    "mech-design": "Makine mühendisliği stajı: CAD ile mekanik parça tasarımı.",
    "pastry": "Pastacılık kursu: temel hamur ve tatlı teknikleri.",
}

# ADR-0002: queries get this instruction; documents get no prefix.
QUERY_PREFIX = (
    "Instruct: Given a student's CV summary, retrieve matching academic opportunities\nQuery: "
)


class CvSummary(BaseModel):
    skills: list[str]
    interests: list[str]


def _stems(text: str) -> set[str]:
    # Same idea as the evaluation harness: compare the first 5 letters of each word, so that
    # "PostgreSQL" matches "postgresql" and "işleme" matches "işlemede".
    return {w[:5] for w in re.findall(r"\w+", text.lower())}


def not_in_cv(items: list[str], cv: str) -> list[str]:
    cv_stems = _stems(cv)
    return [item for item in items if not _stems(item) <= cv_stems]


def cosine(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b, strict=True))
    return dot / math.sqrt(sum(x * x for x in a) * sum(y * y for y in b))


def _headers(key: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {key}"} if key else {}


def llm_spike(client: httpx.Client) -> bool:
    base = os.environ.get("LLM_BASE_URL", "http://localhost:11434/v1").rstrip("/")
    model = os.environ.get("LLM_MODEL", "qwen3.5:4b-q4_K_M")
    effort = os.environ.get("LLM_REASONING_EFFORT", "none")
    body = {
        "model": model,
        "temperature": 0,
        "messages": [
            {
                "role": "user",
                "content": "Extract the skills and the interests from this CV. "
                "Use only items written in the CV.\n\nCV: " + CV_TEXT,
            }
        ],
        "response_format": {
            "type": "json_schema",
            "json_schema": {"name": "cv_summary", "schema": CvSummary.model_json_schema()},
        },
    }
    if effort:
        body["reasoning_effort"] = effort

    print(f"LLM: {model} at {base}")
    start = time.perf_counter()
    resp = client.post(
        f"{base}/chat/completions", json=body, headers=_headers(os.environ.get("LLM_API_KEY", ""))
    )
    seconds = time.perf_counter() - start
    resp.raise_for_status()
    data = resp.json()
    content = data["choices"][0]["message"]["content"]
    try:
        summary = CvSummary.model_validate_json(content)
    except ValidationError as err:
        print(f"  FAIL: the answer does not match the schema\n{err}\n  answer: {content}")
        return False

    usage = data.get("usage", {})
    out_tokens = usage.get("completion_tokens", 0)
    print(f"  schema valid: {summary.model_dump()}")
    print(f"  time {seconds:.1f} s, tokens in {usage.get('prompt_tokens')}, out {out_tokens}")
    invented = not_in_cv(summary.skills + summary.interests, CV_TEXT)
    print(f"  items not in the CV: {invented or 'none'}")
    return True


def embedding_spike(client: httpx.Client) -> bool:
    llm_base = os.environ.get("LLM_BASE_URL", "http://localhost:11434/v1")
    base = os.environ.get("EMBEDDING_BASE_URL", llm_base).rstrip("/")
    model = os.environ.get("EMBEDDING_MODEL", "qwen3-embedding:0.6b")
    key = os.environ.get("EMBEDDING_API_KEY", os.environ.get("LLM_API_KEY", ""))
    texts = [QUERY_PREFIX + CV_TEXT, *OPPORTUNITIES.values()]

    print(f"Embedding: {model} at {base}")
    start = time.perf_counter()
    resp = client.post(
        f"{base}/embeddings", json={"model": model, "input": texts}, headers=_headers(key)
    )
    seconds = time.perf_counter() - start
    resp.raise_for_status()
    vectors = [d["embedding"] for d in sorted(resp.json()["data"], key=lambda d: d["index"])]

    dims = len(vectors[0])
    print(f"  {len(texts)} texts in {seconds:.1f} s, {dims} dimensions")
    if dims != 1024:
        print("  FAIL: the database column has 1024 dimensions (WBS-14.3)")
        return False
    ranking = sorted(
        ((cosine(vectors[0], v), name) for name, v in zip(OPPORTUNITIES, vectors[1:], strict=True)),
        reverse=True,
    )
    for score, name in ranking:
        print(f"  {score:.2f}  {name}")
    return True


def main() -> int:
    with httpx.Client(timeout=300) as client:
        ok = llm_spike(client)
        print()
        ok = embedding_spike(client) and ok
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
