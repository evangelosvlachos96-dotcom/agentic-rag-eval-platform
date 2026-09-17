"""Build and load the per-dataset indexes.

Layout under ``data/processed/<dataset_version>/index/``:

- ``bm25.json``                       tokenized corpus for :class:`BM25Index`
- ``vectors_<embedder slug>.npz``     :class:`NumpyVectorStore` for one embedding model

The vector file doubles as the embedding cache: ``rag index`` skips encoding
when the file for the requested model already exists for that dataset version.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import structlog
from pydantic import BaseModel, ConfigDict

from ragplatform.config import get_settings
from ragplatform.ingestion.chunking import index_text
from ragplatform.ingestion.dataset import read_chunks, read_manifest
from ragplatform.retrieval.bm25 import BM25Index
from ragplatform.retrieval.embedder import embedder_slug
from ragplatform.retrieval.hybrid import HybridRetriever
from ragplatform.retrieval.vector_store import NumpyVectorStore

if TYPE_CHECKING:
    from ragplatform.retrieval.config import RetrievalConfig
    from ragplatform.retrieval.embedder import Embedder
    from ragplatform.retrieval.reranker import Reranker

log = structlog.get_logger(__name__)

INDEX_SUBDIR = "index"
BM25_FILE = "bm25.json"


class IndexReport(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    dataset_version: str
    n_chunks: int
    bm25_path: Path
    vectors_path: Path | None
    embeddings_reused: bool


def bm25_path(dataset_dir: Path) -> Path:
    return dataset_dir / INDEX_SUBDIR / BM25_FILE


def vectors_path(dataset_dir: Path, embedder_name: str) -> Path:
    return dataset_dir / INDEX_SUBDIR / f"vectors_{embedder_slug(embedder_name)}.npz"


def build_index(
    dataset_dir: Path, embedder: Embedder | None = None, *, force: bool = False
) -> IndexReport:
    """Write the BM25 index and, if an embedder is given, the vector store."""
    manifest = read_manifest(dataset_dir)
    chunks = read_chunks(dataset_dir)
    texts = [index_text(chunk) for chunk in chunks]
    ids = [chunk.id for chunk in chunks]

    bm25 = BM25Index.from_texts(ids, texts)
    bm25.save(bm25_path(dataset_dir))
    log.info("bm25_index_built", chunks=len(chunks))

    vectors: Path | None = None
    reused = False
    if embedder is not None:
        vectors = vectors_path(dataset_dir, embedder.name)
        if vectors.exists() and not force:
            reused = True
            log.info("embeddings_cached", path=vectors.as_posix())
        else:
            store = NumpyVectorStore()
            store.add(ids, embedder.embed_documents(texts))
            store.save(vectors)
            log.info("vector_index_built", chunks=len(chunks), model=embedder.name)
    return IndexReport(
        dataset_version=manifest.dataset_version,
        n_chunks=len(chunks),
        bm25_path=bm25_path(dataset_dir),
        vectors_path=vectors,
        embeddings_reused=reused,
    )


def make_embedder(config: RetrievalConfig) -> Embedder:
    """The sentence-transformers embedder named by the config or the settings."""
    from ragplatform.retrieval.embedder import SentenceTransformerEmbedder

    return SentenceTransformerEmbedder(config.embedding_model or get_settings().embedding_model)


def make_reranker(config: RetrievalConfig) -> Reranker:
    from ragplatform.retrieval.reranker import CrossEncoderReranker

    return CrossEncoderReranker(config.reranker_model or get_settings().reranker_model)


def load_retriever(
    config: RetrievalConfig,
    dataset_dir: Path,
    *,
    embedder: Embedder | None = None,
    reranker: Reranker | None = None,
) -> HybridRetriever:
    """Load the indexes a config needs. Models are only instantiated when required."""
    chunks = read_chunks(dataset_dir)
    bm25: BM25Index | None = None
    store: NumpyVectorStore | None = None
    if config.uses_bm25:
        path = bm25_path(dataset_dir)
        if not path.exists():
            raise FileNotFoundError(f"{path} missing; run `rag index` first")
        bm25 = BM25Index.load(path)
    if config.uses_vectors:
        embedder = embedder or make_embedder(config)
        path = vectors_path(dataset_dir, embedder.name)
        if not path.exists():
            raise FileNotFoundError(f"{path} missing; run `rag index` first")
        store = NumpyVectorStore.load(path)
    if config.rerank:
        reranker = reranker or make_reranker(config)
    return HybridRetriever(
        config, chunks, bm25=bm25, vector_store=store, embedder=embedder, reranker=reranker
    )
