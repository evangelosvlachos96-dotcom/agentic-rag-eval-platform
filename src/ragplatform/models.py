"""Core data models shared across the platform.

These pydantic models are the contracts between layers: ingestion produces
:class:`Document` and :class:`Chunk`, retrieval produces :class:`RetrievedChunk`,
and generation produces :class:`Answer`. Keeping them in one place means every
layer (and every evaluation) speaks the same schema.

Models are immutable (``frozen=True``) so that they can be safely shared between
pipeline stages without one stage mutating what another already recorded.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class _FrozenModel(BaseModel):
    """Base class: immutable, strict about unknown fields."""

    model_config = ConfigDict(frozen=True, extra="forbid")


class Document(_FrozenModel):
    """A source document before chunking."""

    id: str = Field(min_length=1, description="Stable, unique document identifier.")
    content: str = Field(min_length=1, description="Full text of the document.")
    source: str | None = Field(default=None, description="Origin, e.g. a path or URL.")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Free-form metadata.")


class Chunk(_FrozenModel):
    """A contiguous piece of a document, the unit of retrieval."""

    id: str = Field(min_length=1, description="Stable, unique chunk identifier.")
    document_id: str = Field(min_length=1, description="Parent document id.")
    content: str = Field(min_length=1, description="Chunk text.")
    index: int = Field(ge=0, description="0-based position of the chunk within its document.")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Inherited + chunk-level.")


class RetrievedChunk(_FrozenModel):
    """A chunk returned by a retriever, with its score and provenance."""

    chunk: Chunk
    score: float = Field(description="Retriever-specific relevance score (higher is better).")
    rank: int = Field(ge=1, description="1-based rank in the result list.")
    retriever: str = Field(min_length=1, description="Retriever that produced it, e.g. 'bm25'.")


class Citation(_FrozenModel):
    """A reference from an answer back to a supporting chunk."""

    chunk_id: str = Field(min_length=1)
    quote: str | None = Field(default=None, description="Verbatim supporting span, if known.")


class Answer(_FrozenModel):
    """A generated answer to a query, grounded in retrieved chunks."""

    query: str = Field(min_length=1)
    text: str = Field(description="Answer text; may be empty when abstaining.")
    citations: list[Citation] = Field(default_factory=list)
    abstained: bool = Field(default=False, description="True when the system declined to answer.")
    model: str | None = Field(default=None, description="Model id that produced the answer.")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Latency, tokens, etc.")
