"""Errors of the AI services (WBS-14.5).

Features catch ``AIError`` and start their fallback (US-37, NFR-17), for example the AI search
falls back to the eligible list ranked by embedding similarity.
"""


class AIError(Exception):
    """Base class: the AI call did not give a usable result."""


class AITimeoutError(AIError):
    """The call took longer than its timeout (LLM 12 s, embedding 4 s by default)."""


class AIResponseError(AIError):
    """The provider answered, but the answer is not usable (for example invalid JSON)."""


class AIProviderError(AIError):
    """The provider returned an error. ``retryable`` is True for rate limits and server errors."""

    def __init__(self, message: str, *, retryable: bool) -> None:
        super().__init__(message)
        self.retryable = retryable
