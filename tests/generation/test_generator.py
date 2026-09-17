"""Tests for ragplatform.generation.generator with a fake provider."""

from __future__ import annotations

import json

import pytest

from ragplatform.generation.generator import (
    ABSTAIN_TEXT,
    build_user_message,
    generate_answer,
    validate_citations,
)
from ragplatform.llm.fake import FakeProvider
from ragplatform.llm.structured import StructuredOutputError
from ragplatform.models import Chunk, RetrievedChunk
from ragplatform.pipelines.run_config import GenerationConfig


def _retrieved(chunk_id: str, text: str, rank: int) -> RetrievedChunk:
    chunk = Chunk(
        id=chunk_id,
        document_id="doc",
        content=text,
        index=rank - 1,
        metadata={
            "doc_title": "Widget Transfer Protocol",
            "section_path": "Specification > Framing",
            "char_start": 0,
            "char_end": len(text),
            "token_count": 5,
        },
    )
    return RetrievedChunk(chunk=chunk, score=1.0 / rank, rank=rank, retriever="bm25")


CHUNKS = [
    _retrieved("doc-0001", "Every frame starts with a four byte length.", 1),
    _retrieved("doc-0002", "A length of zero marks the end of the transfer.", 2),
]
CONFIG = GenerationConfig(prompt_version="answer_v1", max_tokens=256)


def test_user_message_wraps_chunks_in_xml_with_ids() -> None:
    message = build_user_message("How do frames start?", CHUNKS)
    assert (
        '<chunk id="doc-0001" source="Widget Transfer Protocol > Specification > Framing">'
        in message
    )
    assert message.count("<chunk id=") == 2
    assert message.endswith("<question>\nHow do frames start?\n</question>")


def test_validate_citations_splits_valid_and_invalid_and_dedupes() -> None:
    valid, invalid = validate_citations(
        ["doc-0002", "doc-9999", "doc-0002", "doc-0001"], {"doc-0001", "doc-0002"}
    )
    assert [c.chunk_id for c in valid] == ["doc-0002", "doc-0001"]
    assert invalid == ["doc-9999"]


async def test_valid_answer_with_citations() -> None:
    reply = json.dumps(
        {
            "answer": "Frames start with a four byte length.",
            "citations": ["doc-0001"],
            "abstain": False,
        }
    )
    provider = FakeProvider(responses=[reply], model_name="fake-1")
    answer = await generate_answer("How do frames start?", CHUNKS, provider, CONFIG, "fake-1")
    assert answer.text == "Frames start with a four byte length."
    assert [c.chunk_id for c in answer.citations] == ["doc-0001"]
    assert answer.abstained is False
    assert answer.invalid_citations == []
    assert answer.model == "fake-1"
    assert answer.prompt_version == "answer_v1"
    assert answer.usage is not None
    assert answer.metadata["repaired"] is False
    request = provider.requests[0]
    assert request.purpose == "answer"
    assert request.max_tokens == 256
    assert "answer only" in request.system.lower() or "only information" in request.system.lower()


async def test_invalid_citations_are_removed_and_flagged() -> None:
    reply = json.dumps({"answer": "x", "citations": ["doc-0002", "made-up"], "abstain": False})
    answer = await generate_answer("q", CHUNKS, FakeProvider(responses=[reply]), CONFIG, "fake")
    assert [c.chunk_id for c in answer.citations] == ["doc-0002"]
    assert answer.invalid_citations == ["made-up"]


async def test_repair_retry_on_malformed_output() -> None:
    good = json.dumps({"answer": "ok", "citations": ["doc-0001"], "abstain": False})
    provider = FakeProvider(responses=["<not json>", good])
    answer = await generate_answer("q", CHUNKS, provider, CONFIG, "fake")
    assert answer.text == "ok"
    assert answer.metadata["repaired"] is True
    assert provider.calls == 2


async def test_unrepairable_output_raises() -> None:
    provider = FakeProvider(responses=["nope", "still nope"])
    with pytest.raises(StructuredOutputError):
        await generate_answer("q", CHUNKS, provider, CONFIG, "fake")


async def test_empty_retrieval_abstains_without_llm_call() -> None:
    provider = FakeProvider(responses=["should never be used"])
    answer = await generate_answer("q", [], provider, CONFIG, "fake")
    assert answer.abstained is True
    assert answer.text == ABSTAIN_TEXT
    assert answer.citations == []
    assert answer.model is None
    assert answer.metadata["reason"] == "empty_retrieval"
    assert provider.calls == 0


async def test_model_abstention_drops_citations() -> None:
    reply = json.dumps({"answer": "Not covered.", "citations": ["doc-0001"], "abstain": True})
    answer = await generate_answer("q", CHUNKS, FakeProvider(responses=[reply]), CONFIG, "fake")
    assert answer.abstained is True
    assert answer.citations == []
