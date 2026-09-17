"""Tests for ragplatform.retrieval.vector_store and the hash embedder."""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
import pytest

from ragplatform.retrieval.embedder import HashEmbedder, embedder_slug, normalize_rows
from ragplatform.retrieval.vector_store import NumpyVectorStore

if TYPE_CHECKING:
    from pathlib import Path


def test_hash_embedder_is_deterministic_and_normalized() -> None:
    embedder = HashEmbedder(dim=32)
    a = embedder.embed_documents(["hello world", "hello hello"])
    b = embedder.embed_documents(["hello world", "hello hello"])
    assert np.array_equal(a, b)
    assert a.shape == (2, 32)
    assert np.allclose(np.linalg.norm(a, axis=1), 1.0)
    assert embedder.embed_query("hello world").shape == (32,)
    assert embedder.name == "hash-32"


def test_normalize_rows_handles_zero_vectors() -> None:
    out = normalize_rows(np.array([[0.0, 0.0], [3.0, 4.0]], dtype=np.float32))
    assert np.allclose(out, [[0.0, 0.0], [0.6, 0.8]])


def test_embedder_slug() -> None:
    assert embedder_slug("BAAI/bge-small-en-v1.5") == "BAAI__bge-small-en-v1.5"


def test_top_k_ordering_and_k_larger_than_store() -> None:
    store = NumpyVectorStore()
    vectors = normalize_rows(np.array([[1.0, 0.0], [0.0, 1.0], [1.0, 1.0]], dtype=np.float32))
    store.add(["x", "y", "xy"], vectors)
    query = normalize_rows(np.array([[1.0, 0.2]], dtype=np.float32))[0]
    results = store.search(query, k=2)
    assert [i for i, _ in results] == ["x", "xy"]
    assert results[0][1] > results[1][1]
    assert [i for i, _ in store.search(query, k=10)] == ["x", "xy", "y"]
    assert store.search(query, k=0) == []
    assert len(store) == 3


def test_ties_keep_insertion_order() -> None:
    store = NumpyVectorStore()
    store.add(["b", "a"], np.array([[1.0, 0.0], [1.0, 0.0]], dtype=np.float32))
    assert [i for i, _ in store.search(np.array([1.0, 0.0], dtype=np.float32), k=2)] == ["b", "a"]


def test_save_and_load_round_trip(tmp_path: Path) -> None:
    embedder = HashEmbedder(dim=16)
    store = NumpyVectorStore()
    store.add(["a", "b"], embedder.embed_documents(["alpha beta", "gamma delta"]))
    path = tmp_path / "index" / "vectors.npz"
    store.save(path)
    loaded = NumpyVectorStore.load(path)
    query = embedder.embed_query("gamma")
    assert loaded.search(query, k=2) == store.search(query, k=2)
    assert loaded.dim == 16
    assert len(loaded) == 2


def test_add_rejects_duplicates_and_length_mismatch() -> None:
    store = NumpyVectorStore()
    store.add(["a"], np.array([[1.0, 0.0]], dtype=np.float32))
    with pytest.raises(ValueError, match="duplicate"):
        store.add(["a"], np.array([[0.0, 1.0]], dtype=np.float32))
    with pytest.raises(ValueError, match="same length"):
        store.add(["b", "c"], np.array([[0.0, 1.0]], dtype=np.float32))


def test_empty_store_search() -> None:
    assert NumpyVectorStore().search(np.array([1.0], dtype=np.float32), k=3) == []
