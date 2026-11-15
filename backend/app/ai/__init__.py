"""AI services foundation (WBS-14.5).

Features use only these two entry points; they never call a provider directly:

    from app.ai import build_embedding_client, build_llm_gateway
    from app.ai.errors import AIError

Unit tests use ``app.ai.testing.FakeLLM`` and ``FakeEmbedder`` instead.
"""

from app.ai.config import AISettings
from app.ai.embeddings import EmbeddingClient, OpenAICompatibleEmbeddingBackend
from app.ai.llm import LLMGateway, LLMResult, OpenAICompatibleChatBackend

__all__ = [
    "AISettings",
    "EmbeddingClient",
    "LLMGateway",
    "LLMResult",
    "build_embedding_client",
    "build_llm_gateway",
]


def build_llm_gateway(settings: AISettings | None = None) -> LLMGateway:
    s = settings or AISettings.from_env()
    return LLMGateway(
        OpenAICompatibleChatBackend(s), timeout_s=s.llm_timeout_s, max_retries=s.llm_max_retries
    )


def build_embedding_client(settings: AISettings | None = None) -> EmbeddingClient:
    s = settings or AISettings.from_env()
    return EmbeddingClient(
        OpenAICompatibleEmbeddingBackend(s),
        dimensions=s.embedding_dimensions,
        timeout_s=s.embedding_timeout_s,
    )
