"""Tests for ragplatform.llm.structured (JSON parsing, validation, repair retry)."""

from __future__ import annotations

import pytest
from pydantic import BaseModel, ConfigDict, ValidationError

from ragplatform.llm.fake import FakeProvider
from ragplatform.llm.provider import CompletionRequest
from ragplatform.llm.structured import (
    StructuredOutputError,
    complete_structured,
    extract_json_object,
    parse_as,
)


class Verdict(BaseModel):
    model_config = ConfigDict(extra="forbid")

    ok: bool
    note: str = ""


def _request() -> CompletionRequest:
    return CompletionRequest.single_turn(model="m", system="s", user="u", purpose="judge")


def test_extract_json_object_strips_fences_and_prose() -> None:
    assert extract_json_object('```json\n{"ok": true}\n```') == '{"ok": true}'
    assert extract_json_object('Sure! {"ok": true, "note": "x"} hope that helps') == (
        '{"ok": true, "note": "x"}'
    )
    with pytest.raises(ValueError, match="no JSON object"):
        extract_json_object("nothing here")


def test_parse_as_validates_schema() -> None:
    assert parse_as('{"ok": false}', Verdict) == Verdict(ok=False)
    with pytest.raises(ValidationError):
        parse_as('{"ok": "maybe"}', Verdict)


async def test_valid_first_reply_needs_no_repair() -> None:
    provider = FakeProvider(responses=['{"ok": true}'])
    verdict, result = await complete_structured(provider, _request(), Verdict)
    assert verdict.ok is True
    assert result.repaired is False
    assert provider.calls == 1


async def test_invalid_first_reply_triggers_one_repair_with_error_context() -> None:
    provider = FakeProvider(responses=["not json at all", '{"ok": true, "note": "fixed"}'])
    verdict, result = await complete_structured(provider, _request(), Verdict)
    assert verdict == Verdict(ok=True, note="fixed")
    assert result.repaired is True
    assert provider.calls == 2
    repair = provider.requests[1]
    assert repair.purpose == "judge_repair"
    assert [m.role for m in repair.messages] == ["user", "assistant", "user"]
    assert repair.messages[1].content == "not json at all"
    assert "not valid" in repair.messages[2].content
    assert result.usage.output_tokens > 0


async def test_second_failure_raises() -> None:
    provider = FakeProvider(responses=['{"ok": 1, "extra": 2}', "{}"])
    with pytest.raises(StructuredOutputError, match="after repair"):
        await complete_structured(provider, _request(), Verdict)
    assert provider.calls == 2
