"""Token usage of AI calls (WBS-14.5, WBS-16.5).

Every call reports one ``Usage`` record, also when it fails, because failed attempts cost
tokens too. The record has counts only: never prompts, answers or other personal data (NFR-07).
"""

import logging
from collections.abc import Callable
from dataclasses import dataclass
from typing import Literal

logger = logging.getLogger("app.ai.usage")


@dataclass(frozen=True)
class Usage:
    feature: str  # the calling feature, for example "cv_summary"
    kind: Literal["llm", "embedding"]
    model: str
    prompt_tokens: int
    completion_tokens: int
    attempts: int
    seconds: float
    ok: bool


UsageSink = Callable[[Usage], None]


def log_usage(usage: Usage) -> None:
    logger.info(
        "ai_call feature=%s kind=%s model=%s ok=%s attempts=%d prompt_tokens=%d "
        "completion_tokens=%d seconds=%.2f",
        usage.feature,
        usage.kind,
        usage.model,
        usage.ok,
        usage.attempts,
        usage.prompt_tokens,
        usage.completion_tokens,
        usage.seconds,
    )
