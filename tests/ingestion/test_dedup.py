"""Tests for ragplatform.ingestion.dedup."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ragplatform.ingestion.chunking import ChunkingConfig, ChunkMetadata, chunk_document
from ragplatform.ingestion.dedup import DedupConfig, dedup_chunks
from ragplatform.ingestion.loaders import load_file
from ragplatform.models import Chunk

if TYPE_CHECKING:
    from pathlib import Path


def _chunk(cid: str, text: str) -> Chunk:
    return Chunk(id=cid, document_id="d", content=text, index=0)


def test_exact_duplicates_removed_ignoring_case_and_whitespace() -> None:
    chunks = [_chunk("a", "Hello  World"), _chunk("b", "hello world"), _chunk("c", "Other")]
    kept, report = dedup_chunks(chunks)
    assert [c.id for c in kept] == ["a", "c"]
    assert report.exact_removed == 1
    assert report.near_removed == 0
    assert report.removed[0].duplicate_of == "a"
    assert report.removed[0].kind == "exact"


def test_near_duplicate_paragraph_across_fixture_documents(fixture_corpus_dir: Path) -> None:
    chunks: list[Chunk] = []
    for name in ("widget-protocol.rst", "gadget-guide.md", "release-notes.txt"):
        chunks.extend(chunk_document(load_file(fixture_corpus_dir / name), ChunkingConfig()))
    kept, report = dedup_chunks(chunks, DedupConfig(threshold=0.8))
    assert report.exact_removed == 0
    assert report.near_removed == 1
    removed = report.removed[0]
    kept_ids = {c.id for c in kept}
    assert removed.chunk_id not in kept_ids
    assert removed.duplicate_of in kept_ids
    by_id = {c.id: c for c in chunks}
    assert ChunkMetadata.from_chunk(by_id[removed.chunk_id]).section_path == "Rationale"
    assert ChunkMetadata.from_chunk(by_id[removed.duplicate_of]).section_path == "Rationale"
    # The first occurrence in corpus order survives: here the .rst copy was seen first.
    assert by_id[removed.duplicate_of].content.endswith("trivial to fuzz.")
    assert by_id[removed.chunk_id].content.endswith("to fuzz and to test.")


def test_unrelated_chunks_are_all_kept() -> None:
    chunks = [
        _chunk(str(i), f"completely different text number {i} about topic {i * 7}")
        for i in range(5)
    ]
    kept, report = dedup_chunks(chunks)
    assert len(kept) == 5
    assert report.removed == []


def test_empty_input() -> None:
    kept, report = dedup_chunks([])
    assert kept == []
    assert report.kept == 0
