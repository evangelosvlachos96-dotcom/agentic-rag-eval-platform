"""Tests for ragplatform.retrieval.hybrid and index build/load on the fixture corpus."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from ragplatform.ingestion.chunking import ChunkMetadata, index_text
from ragplatform.ingestion.dataset import read_chunks
from ragplatform.ingestion.pipeline import ingest_directory
from ragplatform.retrieval.bm25 import BM25Index
from ragplatform.retrieval.config import RetrievalConfig
from ragplatform.retrieval.embedder import HashEmbedder
from ragplatform.retrieval.hybrid import HybridRetriever
from ragplatform.retrieval.index import build_index, load_retriever
from ragplatform.retrieval.reranker import NoOpReranker
from ragplatform.retrieval.vector_store import NumpyVectorStore

if TYPE_CHECKING:
    from pathlib import Path

    from ragplatform.models import Chunk


@pytest.fixture
def dataset_dir(fixture_corpus_dir: Path, tmp_path: Path) -> Path:
    return ingest_directory(fixture_corpus_dir, tmp_path / "processed").output_dir


@pytest.fixture
def chunks(dataset_dir: Path) -> list[Chunk]:
    return read_chunks(dataset_dir)


def _retriever(chunks: list[Chunk], config: RetrievalConfig) -> HybridRetriever:
    embedder = HashEmbedder(dim=64)
    store = NumpyVectorStore()
    store.add([c.id for c in chunks], embedder.embed_documents([index_text(c) for c in chunks]))
    bm25 = BM25Index.from_texts([c.id for c in chunks], [index_text(c) for c in chunks])
    return HybridRetriever(
        config,
        chunks,
        bm25=bm25,
        vector_store=store,
        embedder=embedder,
        reranker=NoOpReranker(),
    )


def test_bm25_mode_records_only_bm25_stage(chunks: list[Chunk]) -> None:
    retriever = _retriever(chunks, RetrievalConfig(mode="bm25", final_k=3))
    results = retriever.retrieve("ZX-9000-ALPHA heartbeat")
    assert results
    assert results[0].retriever == "bm25"
    assert [r.rank for r in results] == list(range(1, len(results) + 1))
    assert set(results[0].stages) == {"bm25"}
    assert ChunkMetadata.from_chunk(results[0].chunk).section_path == "Specification > Framing"


def test_vector_mode_records_only_vector_stage(chunks: list[Chunk]) -> None:
    retriever = _retriever(chunks, RetrievalConfig(mode="vector", final_k=2))
    results = retriever.retrieve("mounting the hinges with screws")
    assert len(results) == 2
    assert set(results[0].stages) == {"vector"}
    assert results[0].stages["vector"].rank == 1
    assert results[0].score == results[0].stages["vector"].score


def test_hybrid_mode_fuses_and_reranks(chunks: list[Chunk]) -> None:
    config = RetrievalConfig(mode="hybrid", candidate_k=10, rerank=True, final_k=4)
    retriever = _retriever(chunks, config)
    results = retriever.retrieve("heartbeat frame every thirty seconds")
    assert len(results) == 4
    assert results[0].retriever == "hybrid+rerank"
    top = results[0]
    assert "fused" in top.stages
    assert "rerank" in top.stages
    assert "bm25" in top.stages or "vector" in top.stages
    # NoOpReranker keeps the fused order, so rerank rank == fused rank for the top hit.
    assert top.stages["rerank"].rank == top.stages["fused"].rank == 1
    assert ChunkMetadata.from_chunk(top.chunk).section_path == "Specification > Framing"


def test_final_k_and_candidate_k_limit_results(chunks: list[Chunk]) -> None:
    config = RetrievalConfig(mode="hybrid", candidate_k=2, final_k=8)
    results = _retriever(chunks, config).retrieve("frame")
    assert len(results) <= 2


def test_missing_components_are_rejected(chunks: list[Chunk]) -> None:
    with pytest.raises(ValueError, match="BM25"):
        HybridRetriever(RetrievalConfig(mode="bm25"), chunks)
    with pytest.raises(ValueError, match="vector store"):
        HybridRetriever(RetrievalConfig(mode="vector"), chunks)
    with pytest.raises(ValueError, match="reranker"):
        HybridRetriever(
            RetrievalConfig(mode="bm25", rerank=True),
            chunks,
            bm25=BM25Index.from_texts(["a"], ["text"]),
        )


def test_build_index_and_load_retriever_round_trip(dataset_dir: Path) -> None:
    embedder = HashEmbedder(dim=32)
    report = build_index(dataset_dir, embedder)
    assert report.bm25_path.exists()
    assert report.vectors_path is not None
    assert report.vectors_path.exists()
    assert report.embeddings_reused is False
    # Second build reuses the cached embeddings for the same dataset version.
    assert build_index(dataset_dir, embedder).embeddings_reused is True
    assert build_index(dataset_dir, embedder, force=True).embeddings_reused is False

    retriever = load_retriever(
        RetrievalConfig(mode="hybrid", rerank=True),
        dataset_dir,
        embedder=embedder,
        reranker=NoOpReranker(),
    )
    results = retriever.retrieve("ZX-9000-ALPHA")
    assert results
    assert ChunkMetadata.from_chunk(results[0].chunk).section_path == "Specification > Framing"


def test_load_retriever_requires_index(dataset_dir: Path) -> None:
    with pytest.raises(FileNotFoundError, match="rag index"):
        load_retriever(RetrievalConfig(mode="bm25"), dataset_dir)
