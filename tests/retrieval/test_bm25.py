"""Tests for ragplatform.retrieval.bm25."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from ragplatform.ingestion.chunking import ChunkMetadata, chunk_document, index_text
from ragplatform.ingestion.loaders import load_file
from ragplatform.retrieval.bm25 import BM25Index, tokenize

if TYPE_CHECKING:
    from pathlib import Path

    from ragplatform.models import Chunk


def _fixture_chunks(fixture_corpus_dir: Path) -> list[Chunk]:
    chunks: list[Chunk] = []
    for path in sorted(fixture_corpus_dir.iterdir()):
        chunks.extend(chunk_document(load_file(path)))
    return chunks


def test_tokenizer_lowercases_and_keeps_identifiers_whole() -> None:
    assert tokenize("PEP-484 and __future__") == ["pep-484", "pep", "484", "and", "__future__"]
    assert tokenize("typing.List") == ["typing.list", "typing", "list"]
    assert tokenize("ZX-9000-ALPHA!") == ["zx-9000-alpha", "zx", "9000", "alpha"]
    assert tokenize("") == []
    assert tokenize("...") == []


def test_exact_term_query_retrieves_the_framing_section(fixture_corpus_dir: Path) -> None:
    chunks = _fixture_chunks(fixture_corpus_dir)
    index = BM25Index.from_texts([c.id for c in chunks], [index_text(c) for c in chunks])
    results = index.search("ZX-9000-ALPHA", k=3)
    assert results, "exact identifier should match"
    top_id, top_score = results[0]
    top = next(c for c in chunks if c.id == top_id)
    assert ChunkMetadata.from_chunk(top).section_path == "Specification > Framing"
    assert ChunkMetadata.from_chunk(top).doc_title == "Widget Transfer Protocol"
    assert top_score > 0
    # Only one chunk contains the identifier, and a partial term ("alpha") is not
    # elsewhere either, so the result list has exactly one positive-score hit.
    assert len(results) == 1


def test_search_returns_only_positive_scores_in_descending_order(
    fixture_corpus_dir: Path,
) -> None:
    chunks = _fixture_chunks(fixture_corpus_dir)
    index = BM25Index.from_texts([c.id for c in chunks], [index_text(c) for c in chunks])
    results = index.search("screws hinges frame", k=50)
    scores = [s for _, s in results]
    assert scores == sorted(scores, reverse=True)
    assert all(s > 0 for s in scores)
    assert len(results) < len(chunks)
    assert index.search("screws", k=0) == []
    assert index.search("!!!", k=5) == []


def test_save_and_load_round_trip(fixture_corpus_dir: Path, tmp_path: Path) -> None:
    chunks = _fixture_chunks(fixture_corpus_dir)
    index = BM25Index.from_texts([c.id for c in chunks], [index_text(c) for c in chunks])
    path = tmp_path / "idx" / "bm25.json"
    index.save(path)
    loaded = BM25Index.load(path)
    assert len(loaded) == len(index)
    assert loaded.search("heartbeat frame", k=5) == index.search("heartbeat frame", k=5)


def test_index_rejects_empty_or_mismatched_input() -> None:
    with pytest.raises(ValueError, match="at least one"):
        BM25Index([], [])
    with pytest.raises(ValueError, match="same length"):
        BM25Index(["a"], [])
