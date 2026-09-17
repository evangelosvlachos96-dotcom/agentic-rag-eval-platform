"""Anthropic implementation of :class:`LLMProvider` (async, SDK-managed retries).

This is the only module in the code base that imports the ``anthropic`` SDK.
Retries for rate limits, 5xx responses and connection errors are delegated to
the SDK's built-in exponential backoff (``max_retries``); a fuller async batch
runner with its own retry policy is planned for Milestone 8.

Sampling parameters (temperature, top_p) are not sent: current Claude models
and SDK 1.x no longer accept them. Judge repeatability comes from fixed
prompts plus the disk cache, not from a temperature setting.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import anthropic
import structlog
from anthropic import omit

from ragplatform.llm.provider import CompletionRequest, CompletionResponse, LLMError
from ragplatform.models import TokenUsage

if TYPE_CHECKING:
    from anthropic.types import MessageParam

    from ragplatform.config import Settings

log = structlog.get_logger(__name__)


class AnthropicProvider:
    """Thin wrapper over ``anthropic.AsyncAnthropic``."""

    def __init__(self, api_key: str, max_retries: int = 3, timeout_seconds: float = 120.0) -> None:
        self._client = anthropic.AsyncAnthropic(
            api_key=api_key, max_retries=max_retries, timeout=timeout_seconds
        )

    @classmethod
    def from_settings(cls, settings: Settings) -> AnthropicProvider:
        if settings.anthropic_api_key is None or not settings.has_anthropic_key:
            raise LLMError("ANTHROPIC_API_KEY is not configured")
        return cls(settings.anthropic_api_key.get_secret_value())

    @property
    def name(self) -> str:
        return "anthropic"

    async def complete(self, request: CompletionRequest) -> CompletionResponse:
        messages: list[MessageParam] = [
            {"role": m.role, "content": m.content} for m in request.messages
        ]
        try:
            response = await self._client.messages.create(
                model=request.model,
                max_tokens=request.max_tokens,
                system=request.system or omit,
                messages=messages,
            )
        except anthropic.APIError as exc:
            raise LLMError(f"anthropic call failed ({request.purpose}): {exc}") from exc
        if response.stop_reason == "refusal":
            raise LLMError(f"model refused the request ({request.purpose})")
        text = "".join(block.text for block in response.content if block.type == "text")
        usage = TokenUsage(
            input_tokens=response.usage.input_tokens, output_tokens=response.usage.output_tokens
        )
        log.debug(
            "llm_call",
            purpose=request.purpose,
            model=response.model,
            input_tokens=usage.input_tokens,
            output_tokens=usage.output_tokens,
            stop_reason=response.stop_reason,
        )
        return CompletionResponse(
            text=text, model=response.model, usage=usage, stop_reason=response.stop_reason
        )
