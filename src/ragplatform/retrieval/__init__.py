"""Retrieval: finding the chunks most relevant to a query.

Responsibilities (Milestone 3):

- ``embedder``: :class:`Embedder` protocol; sentence-transformers default, hash embedder for tests
- ``vector_store``: :class:`VectorStore` protocol; exact numpy cosine search with save/load
- ``bm25``: lexical index with an identifier-preserving tokenizer
- ``fusion``: Reciprocal Rank Fusion as a pure function
- ``reranker``: :class:`Reranker` protocol; cross-encoder default and a no-op
- ``config``: :class:`RetrievalConfig` (mode, candidate_k, rerank, final_k)
- ``hybrid``: :class:`HybridRetriever` wiring the stages and recording per-stage scores
- ``index``: build / load the per-dataset-version indexes
"""

from ragplatform.retrieval.bm25 import BM25Index, tokenize
from ragplatform.retrieval.config import RetrievalConfig
from ragplatform.retrieval.embedder import Embedder, HashEmbedder
from ragplatform.retrieval.fusion import reciprocal_rank_fusion
from ragplatform.retrieval.hybrid import HybridRetriever
from ragplatform.retrieval.index import build_index, load_retriever
from ragplatform.retrieval.reranker import NoOpReranker, Reranker
from ragplatform.retrieval.vector_store import NumpyVectorStore, VectorStore

__all__ = [
    "BM25Index",
    "Embedder",
    "HashEmbedder",
    "HybridRetriever",
    "NoOpReranker",
    "NumpyVectorStore",
    "Reranker",
    "RetrievalConfig",
    "VectorStore",
    "build_index",
    "load_retriever",
    "reciprocal_rank_fusion",
    "tokenize",
]
