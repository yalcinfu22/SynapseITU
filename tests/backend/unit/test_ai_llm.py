"""WBS-14.5: LLM gateway. All tests use the fake LLM or a mocked HTTP transport, never a real model."""

import json
import logging

import httpx
import pytest
from pydantic import BaseModel

from app.ai.config import AISettings
from app.ai.errors import AIProviderError, AIResponseError, AITimeoutError
from app.ai.llm import LLMGateway, OpenAICompatibleChatBackend
from app.ai.testing import FakeLLM


class CvSummary(BaseModel):
    skills: list[str]
    interests: list[str]


VALID = '{"skills": ["Python"], "interests": ["NLP"]}'


def gateway(fake: FakeLLM, **kwargs) -> LLMGateway:
    return LLMGateway(fake, **({"timeout_s": 5, "max_retries": 2} | kwargs))


# ---- gateway behaviour -------------------------------------------------------------------


async def test_valid_answer_is_parsed_into_the_schema():
    result = await gateway(FakeLLM([VALID])).call("Summarize this CV", CvSummary, feature="test")
    assert result.output == CvSummary(skills=["Python"], interests=["NLP"])
    assert result.attempts == 1


async def test_invalid_answer_is_retried_with_feedback():
    fake = FakeLLM(['{"skills": "Python"}', VALID])
    result = await gateway(fake).call("Summarize this CV", CvSummary, feature="test")
    assert result.output.skills == ["Python"]
    assert result.attempts == 2
    retry_messages = fake.calls[1]["messages"]
    assert retry_messages[-2] == {"role": "assistant", "content": '{"skills": "Python"}'}
    assert "schema" in retry_messages[-1]["content"]


async def test_invalid_answers_raise_after_the_last_retry():
    fake = FakeLLM(["not json"] * 3)
    with pytest.raises(AIResponseError):
        await gateway(fake, max_retries=2).call("Summarize", CvSummary, feature="test")
    assert len(fake.calls) == 3


async def test_transient_provider_error_is_retried():
    fake = FakeLLM([AIProviderError("503", retryable=True), VALID])
    result = await gateway(fake).call("Summarize", CvSummary, feature="test")
    assert result.attempts == 2


async def test_permanent_provider_error_is_not_retried():
    fake = FakeLLM([AIProviderError("401 bad key", retryable=False), VALID])
    with pytest.raises(AIProviderError):
        await gateway(fake).call("Summarize", CvSummary, feature="test")
    assert len(fake.calls) == 1


async def test_slow_answer_raises_timeout_so_the_feature_can_fall_back():
    fake = FakeLLM([VALID], delay_s=1.0)
    with pytest.raises(AITimeoutError):
        await gateway(fake, timeout_s=0.05).call("Summarize", CvSummary, feature="test")


async def test_timeout_covers_all_retries_together():
    fake = FakeLLM(["not json", "not json", VALID], delay_s=0.04)
    with pytest.raises(AITimeoutError):
        await gateway(fake, timeout_s=0.1).call("Summarize", CvSummary, feature="test")


async def test_token_usage_of_all_attempts_is_recorded():
    records = []
    fake = FakeLLM(["not json", VALID], prompt_tokens=100, completion_tokens=20)
    await gateway(fake, on_usage=records.append).call("Summarize", CvSummary, feature="cv")
    [usage] = records
    assert (usage.feature, usage.kind, usage.model) == ("cv", "llm", "fake-llm")
    assert (usage.prompt_tokens, usage.completion_tokens, usage.attempts) == (200, 40, 2)


async def test_usage_is_also_recorded_when_the_call_fails():
    records = []
    with pytest.raises(AIResponseError):
        await gateway(FakeLLM(["x"] * 3), on_usage=records.append).call(
            "Summarize", CvSummary, feature="cv"
        )
    assert records[0].attempts == 3
    assert records[0].ok is False


async def test_default_usage_log_has_counts_but_no_prompt_text(caplog):
    caplog.set_level(logging.INFO, logger="app.ai.usage")
    await gateway(FakeLLM([VALID])).call("SECRET CV TEXT", CvSummary, feature="cv")
    assert "feature=cv" in caplog.text
    assert "SECRET CV TEXT" not in caplog.text


async def test_system_prompt_comes_first():
    fake = FakeLLM([VALID])
    await gateway(fake).call("CV", CvSummary, feature="t", system="You extract skills.")
    assert fake.calls[0]["messages"][0] == {"role": "system", "content": "You extract skills."}


# ---- OpenAI-compatible HTTP backend ------------------------------------------------------


def settings(**kwargs) -> AISettings:
    return AISettings.from_env({"LLM_BASE_URL": "http://llm.test/v1", "LLM_MODEL": "m"} | kwargs)


def chat_reply(content: str, prompt_tokens: int = 7, completion_tokens: int = 3) -> dict:
    return {
        "model": "m",
        "choices": [{"message": {"role": "assistant", "content": content}}],
        "usage": {"prompt_tokens": prompt_tokens, "completion_tokens": completion_tokens},
    }


def backend_with(handler, **env) -> OpenAICompatibleChatBackend:
    client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    return OpenAICompatibleChatBackend(settings(**env), client=client)


async def test_http_backend_sends_an_openai_compatible_request():
    seen = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["url"] = str(request.url)
        seen["auth"] = request.headers.get("authorization")
        seen["body"] = json.loads(request.content)
        return httpx.Response(200, json=chat_reply(VALID))

    backend = backend_with(handler, LLM_API_KEY="k")
    reply = await backend.complete([{"role": "user", "content": "hi"}], CvSummary)

    assert seen["url"] == "http://llm.test/v1/chat/completions"
    assert seen["auth"] == "Bearer k"
    assert seen["body"]["model"] == "m"
    assert seen["body"]["reasoning_effort"] == "none"
    assert seen["body"]["response_format"]["type"] == "json_schema"
    assert seen["body"]["response_format"]["json_schema"]["schema"]["required"] == [
        "skills",
        "interests",
    ]
    assert (reply.content, reply.prompt_tokens, reply.completion_tokens) == (VALID, 7, 3)


async def test_http_backend_omits_empty_reasoning_effort_and_missing_key():
    seen = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["auth"] = request.headers.get("authorization")
        seen["body"] = json.loads(request.content)
        return httpx.Response(200, json=chat_reply(VALID))

    await backend_with(handler, LLM_REASONING_EFFORT="").complete([], CvSummary)
    assert "reasoning_effort" not in seen["body"]
    assert seen["auth"] is None


@pytest.mark.parametrize(
    ("status", "retryable"), [(429, True), (500, True), (503, True), (400, False), (401, False)]
)
async def test_http_backend_marks_which_errors_can_be_retried(status, retryable):
    backend = backend_with(lambda request: httpx.Response(status, text="error"))
    with pytest.raises(AIProviderError) as err:
        await backend.complete([], CvSummary)
    assert err.value.retryable is retryable


async def test_http_backend_turns_a_network_timeout_into_ai_timeout():
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout("slow", request=request)

    with pytest.raises(AITimeoutError):
        await backend_with(handler).complete([], CvSummary)


async def test_http_backend_rejects_an_answer_without_content():
    reply = {"choices": [{"message": {"content": None}}], "usage": {}}
    backend = backend_with(lambda request: httpx.Response(200, json=reply))
    with pytest.raises(AIResponseError):
        await backend.complete([], CvSummary)


# ---- settings ----------------------------------------------------------------------------


def test_settings_defaults_follow_the_requirements():
    s = AISettings.from_env({})
    assert s.llm_timeout_s == 12  # NFR-17
    assert s.embedding_timeout_s == 4  # NFR-17
    assert s.embedding_dimensions == 1024  # WBS-14.3 column
    assert s.llm_base_url == s.embedding_base_url == "http://localhost:11434/v1"


def test_settings_read_overrides_from_the_environment():
    s = AISettings.from_env(
        {
            "LLM_TIMEOUT_SECONDS": "60",
            "LLM_MAX_RETRIES": "1",
            "LLM_API_KEY": "k",
            "EMBEDDING_BASE_URL": "http://emb.test/v1",
        }
    )
    assert (s.llm_timeout_s, s.llm_max_retries) == (60, 1)
    assert s.embedding_base_url == "http://emb.test/v1"
    assert s.embedding_api_key == "k"  # falls back to the LLM key


def test_settings_repr_hides_the_api_keys():
    assert "secret-key" not in repr(AISettings.from_env({"LLM_API_KEY": "secret-key"}))
