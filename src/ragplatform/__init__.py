"""agentic-rag-eval-platform.

A production-style agentic RAG system with hybrid retrieval, reranking, a
tool-using agent, and a rigorous evaluation and data-quality layer.

Public surface at this milestone: the core data models and the settings object.
"""

from ragplatform.config import Settings, get_settings
from ragplatform.models import Answer, Chunk, Citation, Document, RetrievedChunk

__version__ = "0.1.0"

__all__ = [
    "Answer",
    "Chunk",
    "Citation",
    "Document",
    "RetrievedChunk",
    "Settings",
    "__version__",
    "get_settings",
]
