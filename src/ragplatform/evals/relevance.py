"""Matching retrieved chunks against source-level relevance labels."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ragplatform.ingestion.chunking import SECTION_SEPARATOR, ChunkMetadata

if TYPE_CHECKING:
    from collections.abc import Iterable, Sequence

    from ragplatform.evals.models import SourceRef
    from ragplatform.models import Chunk, RetrievedChunk


def section_matches(section_path: str, labeled_path: str) -> bool:
    """True when ``section_path`` equals or is nested under ``labeled_path``.

    An empty labeled path matches every section of the document.
    """
    if labeled_path == "":
        return True
    return section_path == labeled_path or section_path.startswith(labeled_path + SECTION_SEPARATOR)


def chunk_is_relevant(chunk: Chunk, sources: Sequence[SourceRef]) -> bool:
    section_path = ChunkMetadata.from_chunk(chunk).section_path
    return any(
        chunk.document_id == source.doc_id and section_matches(section_path, source.section_path)
        for source in sources
    )


def relevance_flags(
    retrieved: Sequence[RetrievedChunk], sources: Sequence[SourceRef]
) -> list[bool]:
    """One flag per retrieved chunk, in rank order."""
    return [chunk_is_relevant(r.chunk, sources) for r in retrieved]


def count_relevant_chunks(chunks: Iterable[Chunk], sources: Sequence[SourceRef]) -> int:
    """How many chunks in the corpus match the labels: the recall denominator."""
    return sum(1 for chunk in chunks if chunk_is_relevant(chunk, sources))
