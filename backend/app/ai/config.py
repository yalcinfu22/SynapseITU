"""Settings of the AI services, read from environment variables (WBS-14.5).

The code never names a provider: the address, the model and the key decide where calls go
(ADR-0001, ADR-0002). The defaults are a local Ollama; staging and production set the variables
as secrets. See ``backend/.env.example``.
"""

import os
from collections.abc import Mapping
from dataclasses import dataclass, field

OLLAMA_URL = "http://localhost:11434/v1"


@dataclass(frozen=True)
class AISettings:
    llm_base_url: str = OLLAMA_URL
    llm_model: str = "qwen3.5:4b-q4_K_M"
    llm_api_key: str = field(default="", repr=False)
    llm_timeout_s: float = 12  # NFR-17
    llm_max_retries: int = 2
    # "none" turns off Qwen thinking; an empty value leaves the field out of the request.
    llm_reasoning_effort: str = "none"
    embedding_base_url: str = OLLAMA_URL
    embedding_model: str = "qwen3-embedding:0.6b"
    embedding_api_key: str = field(default="", repr=False)
    embedding_timeout_s: float = 4  # NFR-17
    embedding_dimensions: int = 1024  # database column (WBS-14.3)

    @classmethod
    def from_env(cls, env: Mapping[str, str] | None = None) -> "AISettings":
        env = os.environ if env is None else env
        d = cls()
        llm_url = env.get("LLM_BASE_URL", d.llm_base_url)
        llm_key = env.get("LLM_API_KEY", d.llm_api_key)
        return cls(
            llm_base_url=llm_url,
            llm_model=env.get("LLM_MODEL", d.llm_model),
            llm_api_key=llm_key,
            llm_timeout_s=float(env.get("LLM_TIMEOUT_SECONDS", d.llm_timeout_s)),
            llm_max_retries=int(env.get("LLM_MAX_RETRIES", d.llm_max_retries)),
            llm_reasoning_effort=env.get("LLM_REASONING_EFFORT", d.llm_reasoning_effort),
            embedding_base_url=env.get("EMBEDDING_BASE_URL", llm_url),
            embedding_model=env.get("EMBEDDING_MODEL", d.embedding_model),
            embedding_api_key=env.get("EMBEDDING_API_KEY", llm_key),
            embedding_timeout_s=float(env.get("EMBEDDING_TIMEOUT_SECONDS", d.embedding_timeout_s)),
            embedding_dimensions=int(env.get("EMBEDDING_DIMENSIONS", d.embedding_dimensions)),
        )
