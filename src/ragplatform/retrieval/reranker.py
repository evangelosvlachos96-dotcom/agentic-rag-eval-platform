"""Reranker interface: cross-encoder default plus a no-op for tests and ablations.

A cross-encoder reads the query and the passage together and is far more
accurate than the bi-encoder used for first-stage retrieval, but it costs one
forward pass per candidate, so it only runs on the ``candidate_k`` fused
results. The passage text given to the model is the chunk's index text
(``title > section`` header plus content) so that short chunks keep their
context.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

from ragplatform.ingestion.chunking import index_text

if TYPE_CHECKING:
    from collections.abc import Sequence

    from ragplatform.models import Chunk


class Reranker(Protocol):
    """Scores candidate chunks against a query and returns them best first."""

    @property
    def name(self) -> str: ...

    def rerank(self, query: str, chunks: Sequence[Chunk]) -> list[tuple[str, float]]:
        """``(chunk_id, score)`` for every input chunk, sorted by score descending."""
        ...


class NoOpReranker:
    """Keeps the incoming order; scores are the reversed positions so ranks stay explicit."""

    @property
    def name(self) -> str:
        return "noop"

    def rerank(self, query: str, chunks: Sequence[Chunk]) -> list[tuple[str, float]]:
        return [(chunk.id, float(len(chunks) - i)) for i, chunk in enumerate(chunks)]


class CrossEncoderReranker:
    """sentence-transformers ``CrossEncoder`` (default ``cross-encoder/ms-marco-MiniLM-L-6-v2``)."""

    def __init__(self, model_name: str, batch_size: int = 32) -> None:
        from sentence_transformers import CrossEncoder

        self._model_name = model_name
        self._batch_size = batch_size
        self._model = CrossEncoder(model_name)

    @property
    def name(self) -> str:
        return self._model_name

    def rerank(self, query: str, chunks: Sequence[Chunk]) -> list[tuple[str, float]]:
        if not chunks:
            return []
        pairs = [(query, index_text(chunk)) for chunk in chunks]
        scores = self._model.predict(pairs, batch_size=self._batch_size, show_progress_bar=False)
        scored = [(chunk.id, float(score)) for chunk, score in zip(chunks, scores, strict=True)]
        return sorted(scored, key=lambda pair: -pair[1])
