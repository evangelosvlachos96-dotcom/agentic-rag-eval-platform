"""Embedder interface with a local sentence-transformers default.

Vectors are always L2-normalized so cosine similarity is a plain dot product
in the vector store. :class:`HashEmbedder` is a deterministic, dependency-free
bag-of-words embedder used by unit tests; it is *not* semantically meaningful.
:class:`SentenceTransformerEmbedder` imports ``sentence_transformers`` lazily so
the base install never needs torch.
"""

from __future__ import annotations

import hashlib
import re
from typing import TYPE_CHECKING, Protocol

import numpy as np

if TYPE_CHECKING:
    from collections.abc import Sequence

    from numpy.typing import NDArray

_WORD = re.compile(r"\w+")


class Embedder(Protocol):
    """Maps texts to L2-normalized float32 vectors."""

    @property
    def name(self) -> str: ...

    def embed_documents(self, texts: Sequence[str]) -> NDArray[np.float32]:
        """Return an ``(n, dim)`` array, one row per text."""
        ...

    def embed_query(self, text: str) -> NDArray[np.float32]:
        """Return a ``(dim,)`` vector for a search query."""
        ...


def normalize_rows(matrix: NDArray[np.float32]) -> NDArray[np.float32]:
    norms = np.linalg.norm(matrix, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    return (matrix / norms).astype(np.float32)


def embedder_slug(name: str) -> str:
    """File-system safe model name: ``BAAI/bge-small-en-v1.5`` -> ``BAAI__bge-small-en-v1.5``."""
    return re.sub(r"[^A-Za-z0-9_.-]", "__", name)


class HashEmbedder:
    """Deterministic hashed bag-of-words vectors for tests (no model download)."""

    def __init__(self, dim: int = 64) -> None:
        self.dim = dim

    @property
    def name(self) -> str:
        return f"hash-{self.dim}"

    def embed_documents(self, texts: Sequence[str]) -> NDArray[np.float32]:
        matrix = np.zeros((len(texts), self.dim), dtype=np.float32)
        for row, text in enumerate(texts):
            for word in _WORD.findall(text.lower()):
                digest = hashlib.sha1(word.encode("utf-8"), usedforsecurity=False).digest()
                matrix[row, int.from_bytes(digest[:4], "big") % self.dim] += 1.0
        return normalize_rows(matrix)

    def embed_query(self, text: str) -> NDArray[np.float32]:
        return np.asarray(self.embed_documents([text])[0], dtype=np.float32)


class SentenceTransformerEmbedder:
    """Local sentence-transformers model (default ``BAAI/bge-small-en-v1.5``), batched."""

    def __init__(self, model_name: str, batch_size: int = 64, query_prefix: str = "") -> None:
        from sentence_transformers import SentenceTransformer

        self._model_name = model_name
        self._batch_size = batch_size
        self._query_prefix = query_prefix
        self._model = SentenceTransformer(model_name)

    @property
    def name(self) -> str:
        return self._model_name

    def embed_documents(self, texts: Sequence[str]) -> NDArray[np.float32]:
        vectors = self._model.encode(
            list(texts),
            batch_size=self._batch_size,
            normalize_embeddings=True,
            convert_to_numpy=True,
            show_progress_bar=len(texts) > 200,
        )
        return normalize_rows(np.asarray(vectors, dtype=np.float32))

    def embed_query(self, text: str) -> NDArray[np.float32]:
        return np.asarray(self.embed_documents([self._query_prefix + text])[0], dtype=np.float32)
