"""LLM gateway (WBS-14.5): every LLM call of the platform goes through ``LLMGateway.call``.

    gateway = build_llm_gateway()
    result = await gateway.call(prompt, CvSummary, feature="cv_summary")
    result.output.skills

The gateway validates the answer against the Pydantic schema (NFR-22), retries invalid answers
and provider errors, stops after one total timeout (NFR-17) and reports the token usage.
A feature catches ``AIError`` and starts its fallback (US-37).
"""

import asyncio
import time
from dataclasses import dataclass
from typing import Any, Protocol

import httpx
from pydantic import BaseModel, ValidationError

from app.ai.config import AISettings
from app.ai.errors import AIProviderError, AIResponseError, AITimeoutError
from app.ai.http import post_json
from app.ai.usage import Usage, UsageSink, log_usage

Message = dict[str, str]

RETRY_FEEDBACK = (
    "Your answer does not match the JSON schema: {error}\n"
    "Answer again with only a JSON object that matches the schema."
)


@dataclass(frozen=True)
class ChatReply:
    content: str
    prompt_tokens: int
    completion_tokens: int


class ChatBackend(Protocol):
    """Sends one chat request. ``OpenAICompatibleChatBackend`` in the app, ``FakeLLM`` in tests."""

    model: str

    async def complete(self, messages: list[Message], schema: type[BaseModel]) -> ChatReply: ...


@dataclass(frozen=True)
class LLMResult[T: BaseModel]:
    output: T
    usage: Usage

    @property
    def attempts(self) -> int:
        return self.usage.attempts


class LLMGateway:
    def __init__(
        self,
        backend: ChatBackend,
        *,
        timeout_s: float = 12,
        max_retries: int = 2,
        on_usage: UsageSink = log_usage,
    ) -> None:
        self.backend = backend
        self.timeout_s = timeout_s
        self.max_retries = max_retries
        self.on_usage = on_usage

    async def call[T: BaseModel](
        self, prompt: str, schema: type[T], *, feature: str, system: str | None = None
    ) -> LLMResult[T]:
        messages: list[Message] = [{"role": "system", "content": system}] if system else []
        messages.append({"role": "user", "content": prompt})
        state = {"attempts": 0, "prompt_tokens": 0, "completion_tokens": 0}
        start = time.perf_counter()
        output: T | None = None
        try:
            # One timeout for all attempts together, so a feature never waits longer (NFR-17).
            async with asyncio.timeout(self.timeout_s):
                output = await self._attempts(messages, schema, state)
        except TimeoutError as err:
            raise AITimeoutError(f"LLM call took longer than {self.timeout_s} s") from err
        finally:
            # Also on failure: failed attempts cost tokens too.
            usage = Usage(
                feature=feature,
                kind="llm",
                model=self.backend.model,
                prompt_tokens=state["prompt_tokens"],
                completion_tokens=state["completion_tokens"],
                attempts=state["attempts"],
                seconds=time.perf_counter() - start,
                ok=output is not None,
            )
            self.on_usage(usage)
        return LLMResult(output, usage)

    async def _attempts[T: BaseModel](
        self, messages: list[Message], schema: type[T], state: dict[str, int]
    ) -> T:
        last_error: Exception | None = None
        for _ in range(self.max_retries + 1):
            state["attempts"] += 1
            try:
                reply = await self.backend.complete(messages, schema)
            except AIProviderError as err:
                if not err.retryable:
                    raise
                last_error = err
                continue
            state["prompt_tokens"] += reply.prompt_tokens
            state["completion_tokens"] += reply.completion_tokens
            try:
                return schema.model_validate_json(reply.content)
            except ValidationError as err:
                last_error = err
                feedback = RETRY_FEEDBACK.format(error=_short(err))
                messages = [
                    *messages,
                    {"role": "assistant", "content": reply.content},
                    {"role": "user", "content": feedback},
                ]
        if isinstance(last_error, AIProviderError):
            raise last_error
        raise AIResponseError(
            f"no valid answer after {state['attempts']} attempts: {_short(last_error)}"
        )


def _short(err: Exception | None) -> str:
    """Error text without the input values, which can contain CV data (NFR-07)."""
    if isinstance(err, ValidationError):
        return "; ".join(
            f"{'.'.join(map(str, e['loc'])) or 'answer'}: {e['msg']}" for e in err.errors()
        )
    return str(err)


class OpenAICompatibleChatBackend:
    """``POST {base_url}/chat/completions`` with a JSON-schema response format."""

    def __init__(self, settings: AISettings, client: httpx.AsyncClient | None = None) -> None:
        self.settings = settings
        self.model = settings.llm_model
        self.client = client or httpx.AsyncClient()

    async def complete(self, messages: list[Message], schema: type[BaseModel]) -> ChatReply:
        s = self.settings
        body: dict[str, Any] = {
            "model": s.llm_model,
            "temperature": 0,
            "messages": messages,
            "response_format": {
                "type": "json_schema",
                "json_schema": {"name": schema.__name__, "schema": schema.model_json_schema()},
            },
        }
        if s.llm_reasoning_effort:
            body["reasoning_effort"] = s.llm_reasoning_effort
        url = s.llm_base_url.rstrip("/") + "/chat/completions"
        data = await post_json(self.client, url, s.llm_api_key, body, s.llm_timeout_s)
        try:
            content = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as err:
            raise AIResponseError("the answer has no message") from err
        if not isinstance(content, str) or not content:
            raise AIResponseError("the answer is empty")
        usage = data.get("usage") or {}
        return ChatReply(
            content=content,
            prompt_tokens=usage.get("prompt_tokens") or 0,
            completion_tokens=usage.get("completion_tokens") or 0,
        )
