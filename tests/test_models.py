"""Tests for ragplatform.models."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from ragplatform.models import Answer, Chunk, Citation, Document, RetrievedChunk


def make_chunk(index: int = 0) -> Chunk:
    return Chunk(id=f"doc-1:{index}", document_id="doc-1", content="some text", index=index)


def test_document_round_trips_through_json() -> None:
    doc = Document(id="doc-1", content="hello", source="a.md", metadata={"lang": "en"})
    restored = Document.model_validate_json(doc.model_dump_json())
    assert restored == doc


def test_document_rejects_empty_content() -> None:
    with pytest.raises(ValidationError):
        Document(id="doc-1", content="")


def test_chunk_rejects_negative_index() -> None:
    with pytest.raises(ValidationError):
        Chunk(id="c", document_id="d", content="x", index=-1)


def test_retrieved_chunk_requires_positive_rank() -> None:
    with pytest.raises(ValidationError):
        RetrievedChunk(chunk=make_chunk(), score=0.5, rank=0, retriever="bm25")


def test_models_are_frozen() -> None:
    chunk = make_chunk()
    with pytest.raises(ValidationError):
        chunk.content = "changed"  # type: ignore[misc]
    assert chunk == make_chunk()


def test_models_reject_unknown_fields() -> None:
    with pytest.raises(ValidationError):
        Citation(chunk_id="c", unexpected="field")  # type: ignore[call-arg]


def test_answer_defaults() -> None:
    answer = Answer(query="what?", text="42", citations=[Citation(chunk_id="doc-1:0")])
    assert answer.abstained is False
    assert answer.model is None
    assert answer.citations[0].quote is None


def test_abstained_answer_may_have_empty_text() -> None:
    answer = Answer(query="what?", text="", abstained=True)
    assert answer.abstained is True
    assert answer.citations == []
