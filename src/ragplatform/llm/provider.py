"""The provider protocol: the only LLM surface the rest of the code base sees.

A :class:`CompletionRequest` is a system prompt plus a list of chat messages;
a :class:`CompletionResponse` is the text, the model that produced it and the
token usage. Keeping this surface tiny means the Anthropic client, the on-disk
cache and the fake provider used in tests are interchangeable.
"""

from __future__ import annotations

from typing import Literal, Protocol

from pydantic import BaseModel, ConfigDict, Field

from ragplatform.models import TokenUsage

Role = Literal["user", "assistant"]


class ChatMessage(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    role: Role
    content: str = Field(min_length=1)


class CompletionRequest(BaseModel):
    """Everything that determines an LLM output (and therefore the cache key)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    model: str = Field(min_length=1)
    system: str = Field(default="")
    messages: list[ChatMessage] = Field(min_length=1)
    max_tokens: int = Field(default=4096, ge=1)
    purpose: str = Field(
        default="generic",
        description="What the call is for (answer, judge_faithfulness, ...). Used for "
        "logging, cost reports and by the fake provider to pick a canned reply.",
    )

    @classmethod
    def single_turn(
        cls, *, model: str, system: str, user: str, purpose: str, max_tokens: int = 4096
    ) -> CompletionRequest:
        return cls(
            model=model,
            system=system,
            messages=[ChatMessage(role="user", content=user)],
            max_tokens=max_tokens,
            purpose=purpose,
        )


class CompletionResponse(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    text: str
    model: str
    usage: TokenUsage
    stop_reason: str | None = None
    cached: bool = Field(default=False, description="True when served from the disk cache.")


class LLMError(RuntimeError):
    """Raised when a provider cannot produce a usable completion."""


class LLMProvider(Protocol):
    """Anything that can complete a request."""

    @property
    def name(self) -> str: ...

    async def complete(self, request: CompletionRequest) -> CompletionResponse: ...
