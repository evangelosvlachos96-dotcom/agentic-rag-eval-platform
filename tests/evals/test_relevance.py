"""Tests for source-level relevance matching, including nested section paths."""

from __future__ import annotations

from ragplatform.evals.models import SourceRef
from ragplatform.evals.relevance import (
    chunk_is_relevant,
    count_relevant_chunks,
    relevance_flags,
    section_matches,
)
from ragplatform.models import Chunk, RetrievedChunk


def _chunk(cid: str, doc: str, section: str) -> Chunk:
    return Chunk(
        id=cid,
        document_id=doc,
        content="x",
        index=0,
        metadata={
            "doc_title": "T",
            "section_path": section,
            "char_start": 0,
            "char_end": 1,
            "token_count": 1,
        },
    )


def test_section_matches_exact_nested_and_whole_document() -> None:
    assert section_matches("Specification", "Specification")
    assert section_matches("Specification > Syntax", "Specification")
    assert section_matches("Specification > Syntax > Details", "Specification > Syntax")
    assert not section_matches("Specification", "Specification > Syntax")  # parent is not nested
    assert not section_matches("Specifications", "Specification")  # prefix without separator
    assert not section_matches("Rationale", "Specification")
    assert section_matches("Anything", "")
    assert section_matches("", "")


def test_chunk_is_relevant_requires_doc_and_section() -> None:
    sources = [SourceRef(doc_id="d1", section_path="Spec")]
    assert chunk_is_relevant(_chunk("a", "d1", "Spec > Syntax"), sources)
    assert not chunk_is_relevant(_chunk("b", "d2", "Spec > Syntax"), sources)
    assert not chunk_is_relevant(_chunk("c", "d1", "Rationale"), sources)
    assert chunk_is_relevant(_chunk("d", "d1", "Rationale"), [SourceRef(doc_id="d1")])


def test_relevance_flags_and_corpus_count() -> None:
    sources = [SourceRef(doc_id="d1", section_path="Spec"), SourceRef(doc_id="d2")]
    corpus = [
        _chunk("1", "d1", "Spec"),
        _chunk("2", "d1", "Spec > A"),
        _chunk("3", "d1", "Other"),
        _chunk("4", "d2", "Intro"),
        _chunk("5", "d3", "Spec"),
    ]
    retrieved = [
        RetrievedChunk(chunk=corpus[2], score=1.0, rank=1, retriever="bm25"),
        RetrievedChunk(chunk=corpus[1], score=0.5, rank=2, retriever="bm25"),
        RetrievedChunk(chunk=corpus[3], score=0.1, rank=3, retriever="bm25"),
    ]
    assert relevance_flags(retrieved, sources) == [False, True, True]
    assert count_relevant_chunks(corpus, sources) == 3
    assert count_relevant_chunks(corpus, []) == 0
