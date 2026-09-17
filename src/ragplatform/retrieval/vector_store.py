"""Vector store interface with an exact in-memory numpy implementation.

:class:`NumpyVectorStore` keeps one ``(n, dim)`` float32 matrix of normalized
vectors, so cosine similarity is ``matrix @ query``. Exact search is fine at
this corpus size (thousands of chunks); an approximate index can implement the
same :class:`VectorStore` protocol later. The store saves to a single ``.npz``.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

import numpy as np

if TYPE_CHECKING:
    from collections.abc import Sequence
    from pathlib import Path

    from numpy.typing import NDArray


class VectorStore(Protocol):
    """Stores id -> vector and answers top-k similarity queries."""

    def add(self, ids: Sequence[str], vectors: NDArray[np.float32]) -> None: ...

    def search(self, query: NDArray[np.float32], k: int) -> list[tuple[str, float]]:
        """Top-k ``(id, cosine score)`` pairs, best first."""
        ...

    def save(self, path: Path) -> None: ...

    def __len__(self) -> int: ...


class NumpyVectorStore:
    """Exact cosine search over normalized vectors held in memory."""

    def __init__(self, dim: int | None = None) -> None:
        self._ids: list[str] = []
        self._matrix: NDArray[np.float32] = np.zeros((0, dim or 0), dtype=np.float32)

    @property
    def dim(self) -> int:
        return int(self._matrix.shape[1])

    def __len__(self) -> int:
        return len(self._ids)

    def add(self, ids: Sequence[str], vectors: NDArray[np.float32]) -> None:
        if len(ids) != vectors.shape[0]:
            raise ValueError("ids and vectors must have the same length")
        if len(set(ids)) != len(ids) or set(ids) & set(self._ids):
            raise ValueError("duplicate ids in vector store")
        vectors = np.asarray(vectors, dtype=np.float32)
        if self._matrix.shape[0] == 0:
            self._matrix = vectors.copy()
        else:
            self._matrix = np.vstack([self._matrix, vectors])
        self._ids.extend(ids)

    def search(self, query: NDArray[np.float32], k: int) -> list[tuple[str, float]]:
        if k <= 0 or not self._ids:
            return []
        scores = self._matrix @ np.asarray(query, dtype=np.float32)
        k = min(k, len(self._ids))
        # argsort on (-score, index) keeps ties in insertion order for determinism.
        order = np.lexsort((np.arange(len(scores)), -scores))[:k]
        return [(self._ids[int(i)], float(scores[int(i)])) for i in order]

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        np.savez(path, ids=np.array(self._ids, dtype=str), vectors=self._matrix)

    @classmethod
    def load(cls, path: Path) -> NumpyVectorStore:
        with np.load(path) as data:
            store = cls()
            store._ids = [str(i) for i in data["ids"].tolist()]
            store._matrix = np.asarray(data["vectors"], dtype=np.float32)
        return store
