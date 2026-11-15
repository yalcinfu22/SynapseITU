"""Fakes for unit tests (WBS-14.5). Unit tests never call a real model.

fake = FakeLLM(['{"skills": ["Python"], "interests": []}'])
gateway = LLMGateway(fake)
...
assert fake.calls[0]["messages"][-1]["content"].startswith("Summarize")

embedder = EmbeddingClient(FakeEmbedder())
"""

import asyncio
import hashlib
import math
import random

from pydantic import BaseModel

from app.ai.embeddings import EmbeddingBatch
from app.ai.llm import ChatReply, Message


class FakeLLM:
    """Returns the scripted answers in order. An exception in the list is raised instead."""

    model = "fake-llm"

    def __init__(
        self,
        answers: list[str | Exception],
        *,
        delay_s: float = 0,
        prompt_tokens: int = 10,
        completion_tokens: int = 5,
    ) -> None:
        self.answers = list(answers)
        self.delay_s = delay_s
        self.prompt_tokens = prompt_tokens
        self.completion_tokens = completion_tokens
        self.calls: list[dict] = []

    async def complete(self, messages: list[Message], schema: type[BaseModel]) -> ChatReply:
        self.calls.append({"messages": list(messages), "schema": schema})
        if self.delay_s:
            await asyncio.sleep(self.delay_s)
        if not self.answers:
            raise AssertionError("FakeLLM has no answer left for this call")
        answer = self.answers.pop(0)
        if isinstance(answer, Exception):
            raise answer
        return ChatReply(answer, self.prompt_tokens, self.completion_tokens)


class FakeEmbedder:
    """Gives every text a fixed pseudo-random vector, so the same text gets the same vector."""

    model = "fake-embedder"

    def __init__(self, *, dimensions: int = 1024, delay_s: float = 0) -> None:
        self.dimensions = dimensions
        self.delay_s = delay_s
        self.calls: list[list[str]] = []

    async def embed(self, texts: list[str]) -> EmbeddingBatch:
        self.calls.append(list(texts))
        if self.delay_s:
            await asyncio.sleep(self.delay_s)
        return EmbeddingBatch([self._vector(t) for t in texts], sum(len(t.split()) for t in texts))

    def _vector(self, text: str) -> list[float]:
        rng = random.Random(hashlib.sha256(text.encode()).digest())
        v = [rng.gauss(0, 1) for _ in range(self.dimensions)]
        length = math.sqrt(sum(x * x for x in v))
        return [x / length for x in v]
