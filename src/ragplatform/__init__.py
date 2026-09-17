"""agentic-rag-eval-platform.

A production-style agentic RAG system with hybrid retrieval, reranking, a
tool-using agent, and a rigorous evaluation and data-quality layer.

Public surface: the core data models and the settings object. Subpackages are
imported explicitly (``ragplatform.ingestion``, ``ragplatform.retrieval``, ...).
"""

from ragplatform.config import Settings, get_settings
from ragplatform.models import (
    Answer,
    Chunk,
    Citation,
    Document,
    RetrievedChunk,
    StageScore,
    TokenUsage,
)

__version__ = "0.1.0"

__all__ = [
    "Answer",
    "Chunk",
    "Citation",
    "Document",
    "RetrievedChunk",
    "Settings",
    "StageScore",
    "TokenUsage",
    "__version__",
    "get_settings",
]
