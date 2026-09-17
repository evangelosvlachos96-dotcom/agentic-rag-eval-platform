"""Structured (JSON) outputs validated with pydantic, with one repair retry.

The model is asked to reply with a single JSON object. The reply is stripped of
code fences, parsed and validated against the caller's pydantic type. If that
fails, the invalid reply is sent back once together with the validation error
and a request to return only corrected JSON. A second failure raises
:class:`StructuredOutputError`; callers decide whether that aborts a run or is
recorded as a failed item. This is provider-agnostic, which is what lets the
fake provider exercise the same path in tests.
"""

from __future__ import annotations

import json
from typing import TypeVar

from pydantic import BaseModel, ConfigDict, ValidationError

from ragplatform.llm.provider import (
    ChatMessage,
    CompletionRequest,
    CompletionResponse,
    LLMError,
    LLMProvider,
)
from ragplatform.models import TokenUsage

T = TypeVar("T", bound=BaseModel)

REPAIR_INSTRUCTION = (
    "Your previous reply was not valid for the required JSON schema. Error:\n{error}\n\n"
    "Reply again with ONLY a corrected JSON object and nothing else."
)


class StructuredOutputError(LLMError):
    """The model failed to produce valid JSON even after the repair retry."""


class StructuredResult(BaseModel):
    """A parsed value plus what it cost to get it."""

    model_config = ConfigDict(frozen=True, extra="forbid", arbitrary_types_allowed=True)

    usage: TokenUsage
    model: str
    repaired: bool
    raw_text: str


def extract_json_object(text: str) -> str:
    """Strip markdown fences and any prose around the outermost ``{...}``."""
    stripped = text.strip()
    if stripped.startswith("```"):
        stripped = stripped.split("\n", 1)[1] if "\n" in stripped else ""
        if stripped.rstrip().endswith("```"):
            stripped = stripped.rstrip()[:-3]
    start = stripped.find("{")
    end = stripped.rfind("}")
    if start == -1 or end == -1 or end < start:
        raise ValueError("no JSON object found in model output")
    return stripped[start : end + 1]


def parse_as(text: str, model_type: type[T]) -> T:
    return model_type.model_validate(json.loads(extract_json_object(text)))


async def complete_structured(
    provider: LLMProvider, request: CompletionRequest, model_type: type[T]
) -> tuple[T, StructuredResult]:
    """Run ``request`` and validate the reply as ``model_type``, repairing once."""
    first: CompletionResponse = await provider.complete(request)
    usage = first.usage
    try:
        return parse_as(first.text, model_type), StructuredResult(
            usage=usage, model=first.model, repaired=False, raw_text=first.text
        )
    except (ValueError, ValidationError) as exc:
        error = str(exc)

    repair_request = request.model_copy(
        update={
            "messages": [
                *request.messages,
                ChatMessage(role="assistant", content=first.text or "(empty reply)"),
                ChatMessage(role="user", content=REPAIR_INSTRUCTION.format(error=error)),
            ],
            "purpose": f"{request.purpose}_repair",
        }
    )
    second = await provider.complete(repair_request)
    usage = usage + second.usage
    try:
        return parse_as(second.text, model_type), StructuredResult(
            usage=usage, model=second.model, repaired=True, raw_text=second.text
        )
    except (ValueError, ValidationError) as exc:
        raise StructuredOutputError(
            f"invalid {model_type.__name__} after repair ({request.purpose}): {exc}"
        ) from exc
