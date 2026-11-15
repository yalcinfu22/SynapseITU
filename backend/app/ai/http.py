"""Shared HTTP helper for OpenAI-compatible servers (Ollama, DeepInfra, vLLM and others)."""

from typing import Any

import httpx

from app.ai.errors import AIProviderError, AITimeoutError

# Rate limits and server errors can pass; other errors (bad key, bad request) will not.
RETRYABLE_STATUS = {408, 409, 429}


async def post_json(
    client: httpx.AsyncClient, url: str, api_key: str, body: dict[str, Any], timeout_s: float
) -> dict[str, Any]:
    headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}
    try:
        resp = await client.post(url, json=body, headers=headers, timeout=timeout_s)
    except httpx.TimeoutException as err:
        raise AITimeoutError(f"no answer from {url} within {timeout_s} s") from err
    except httpx.TransportError as err:
        raise AIProviderError(f"cannot reach {url}: {err}", retryable=True) from err
    if resp.status_code >= 400:
        retryable = resp.status_code >= 500 or resp.status_code in RETRYABLE_STATUS
        # The body can contain our prompt, so only the status goes into the message (NFR-07).
        raise AIProviderError(f"{url} returned HTTP {resp.status_code}", retryable=retryable)
    return resp.json()
