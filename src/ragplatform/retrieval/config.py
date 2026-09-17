"""Retrieval configuration (the ``retrieval:`` block of a run config YAML)."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

RetrievalMode = Literal["vector", "bm25", "hybrid"]


class RetrievalConfig(BaseModel):
    """How a query is turned into a ranked list of chunks."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    mode: RetrievalMode = Field(default="hybrid", description="Which first-stage retrievers run.")
    candidate_k: int = Field(default=50, ge=1, description="Candidates per stage before fusion.")
    rerank: bool = Field(default=False, description="Run the cross-encoder on the candidates.")
    final_k: int = Field(default=8, ge=1, description="Chunks returned to the generator.")
    rrf_k: int = Field(default=60, ge=1, description="RRF constant; only used in hybrid mode.")
    embedding_model: str | None = Field(
        default=None, description="Overrides Settings.embedding_model when set."
    )
    reranker_model: str | None = Field(
        default=None, description="Overrides Settings.reranker_model when set."
    )

    @property
    def uses_bm25(self) -> bool:
        return self.mode in ("bm25", "hybrid")

    @property
    def uses_vectors(self) -> bool:
        return self.mode in ("vector", "hybrid")

    @property
    def retriever_name(self) -> str:
        return f"{self.mode}+rerank" if self.rerank else self.mode
