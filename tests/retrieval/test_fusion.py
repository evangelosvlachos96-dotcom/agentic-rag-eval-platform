"""Tests for ragplatform.retrieval.fusion (hand-computed RRF values)."""

from __future__ import annotations

import pytest

from ragplatform.retrieval.fusion import reciprocal_rank_fusion


def test_rrf_hand_computed_example() -> None:
    # k=60. x: 1/61. y: 1/62 + 1/61. z: 1/63 + 1/62.
    fused = reciprocal_rank_fusion([["x", "y", "z"], ["y", "z"]], k=60)
    ids = [i for i, _ in fused]
    scores = dict(fused)
    assert ids == ["y", "z", "x"]
    assert scores["x"] == pytest.approx(1 / 61)
    assert scores["y"] == pytest.approx(1 / 62 + 1 / 61)
    assert scores["z"] == pytest.approx(1 / 63 + 1 / 62)


def test_rrf_small_k_makes_top_ranks_dominate() -> None:
    fused = reciprocal_rank_fusion([["a", "b"], ["b"]], k=1)
    # a: 1/2 = 0.5 ; b: 1/3 + 1/2 = 0.833
    assert [i for i, _ in fused] == ["b", "a"]
    assert dict(fused)["b"] == pytest.approx(1 / 3 + 1 / 2)


def test_rrf_ties_break_by_id() -> None:
    fused = reciprocal_rank_fusion([["b", "a"], ["a", "b"]])
    assert [i for i, _ in fused] == ["a", "b"]


def test_rrf_empty_and_single_list() -> None:
    assert reciprocal_rank_fusion([]) == []
    assert reciprocal_rank_fusion([[], []]) == []
    single = reciprocal_rank_fusion([["a"]], k=60)
    assert [i for i, _ in single] == ["a"]
    assert single[0][1] == pytest.approx(1 / 61)


def test_rrf_rejects_non_positive_k() -> None:
    with pytest.raises(ValueError, match="positive"):
        reciprocal_rank_fusion([["a"]], k=0)
