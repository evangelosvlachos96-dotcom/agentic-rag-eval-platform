"""The hybrid retriever: BM25 and/or vector search, RRF fusion, optional reranking.

Every :class:`~ragplatform.models.RetrievedChunk` carries the score and rank it
received from each stage (``bm25``, ``vector``, ``fused``, ``rerank``) so a
retrieval failure can be traced to the stage that dropped the chunk.
"""

from __future__ import annotations

from collections import defaultdict
from typing import TYPE_CHECKING

from ragplatform.models import RetrievedChunk, StageScore
from ragplatform.retrieval.fusion import reciprocal_rank_fusion

if TYPE_CHECKING:
    from collections.abc import Sequence

    from ragplatform.models import Chunk
    from ragplatform.retrieval.bm25 import BM25Index
    from ragplatform.retrieval.config import RetrievalConfig
    from ragplatform.retrieval.embedder import Embedder
    from ragplatform.retrieval.reranker import Reranker
    from ragplatform.retrieval.vector_store import VectorStore


class HybridRetriever:
    """Configured by :class:`RetrievalConfig`; components are injected so tests can fake them."""

    def __init__(
        self,
        config: RetrievalConfig,
        chunks: Sequence[Chunk],
        *,
        bm25: BM25Index | None = None,
        vector_store: VectorStore | None = None,
        embedder: Embedder | None = None,
        reranker: Reranker | None = None,
    ) -> None:
        if config.uses_bm25 and bm25 is None:
            raise ValueError(f"mode={config.mode!r} needs a BM25 index")
        if config.uses_vectors and (vector_store is None or embedder is None):
            raise ValueError(f"mode={config.mode!r} needs a vector store and an embedder")
        if config.rerank and reranker is None:
            raise ValueError("rerank=true needs a reranker")
        self.config = config
        self._chunks = {chunk.id: chunk for chunk in chunks}
        self._bm25 = bm25
        self._vector_store = vector_store
        self._embedder = embedder
        self._reranker = reranker

    def retrieve(self, query: str) -> list[RetrievedChunk]:
        config = self.config
        stages: dict[str, dict[str, StageScore]] = defaultdict(dict)

        def record(stage: str, results: list[tuple[str, float]]) -> None:
            for rank, (chunk_id, score) in enumerate(results, start=1):
                stages[chunk_id][stage] = StageScore(score=score, rank=rank)

        rankings: list[list[str]] = []
        candidates: list[tuple[str, float]] = []
        if config.uses_bm25 and self._bm25 is not None:
            candidates = self._bm25.search(query, config.candidate_k)
            record("bm25", candidates)
            rankings.append([chunk_id for chunk_id, _ in candidates])
        if config.uses_vectors and self._vector_store is not None and self._embedder is not None:
            candidates = self._vector_store.search(
                self._embedder.embed_query(query), config.candidate_k
            )
            record("vector", candidates)
            rankings.append([chunk_id for chunk_id, _ in candidates])
        if config.mode == "hybrid":
            candidates = reciprocal_rank_fusion(rankings, k=config.rrf_k)[: config.candidate_k]
            record("fused", candidates)

        if config.rerank and self._reranker is not None and candidates:
            candidates = self._reranker.rerank(
                query, [self._chunks[chunk_id] for chunk_id, _ in candidates]
            )
            record("rerank", candidates)

        return [
            RetrievedChunk(
                chunk=self._chunks[chunk_id],
                score=score,
                rank=rank,
                retriever=config.retriever_name,
                stages=dict(stages[chunk_id]),
            )
            for rank, (chunk_id, score) in enumerate(candidates[: config.final_k], start=1)
        ]
