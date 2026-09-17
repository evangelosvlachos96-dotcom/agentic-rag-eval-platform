"""Tests for ragplatform.evals.metrics against hand-computed values."""

from __future__ import annotations

import math

import pytest

from ragplatform.evals.metrics import (
    dcg_at_k,
    hit_at_k,
    mrr,
    ndcg_at_k,
    precision_at_k,
    recall_at_k,
)

# Ranked list: relevant at ranks 1 and 3; the corpus holds 4 relevant chunks.
FLAGS = [True, False, True, False, False]
N_RELEVANT = 4


def test_recall_at_k() -> None:
    assert recall_at_k(FLAGS, N_RELEVANT, 1) == 0.25
    assert recall_at_k(FLAGS, N_RELEVANT, 3) == 0.5
    assert recall_at_k(FLAGS, N_RELEVANT, 10) == 0.5  # k beyond the list is fine
    assert recall_at_k(FLAGS, 0, 3) == 0.0  # labels matched nothing
    assert recall_at_k([True, True], 1, 2) == 1.0  # capped at 1 if labels undercount


def test_precision_at_k() -> None:
    assert precision_at_k(FLAGS, 1) == 1.0
    assert precision_at_k(FLAGS, 3) == pytest.approx(2 / 3)
    assert precision_at_k(FLAGS, 10) == pytest.approx(2 / 10)  # missing ranks are misses
    assert precision_at_k([], 5) == 0.0


def test_hit_at_k() -> None:
    assert hit_at_k(FLAGS, 1) == 1.0
    assert hit_at_k([False, False, True], 2) == 0.0
    assert hit_at_k([False, False, True], 3) == 1.0
    assert hit_at_k([], 3) == 0.0


def test_mrr() -> None:
    assert mrr(FLAGS) == 1.0
    assert mrr([False, False, True]) == pytest.approx(1 / 3)
    assert mrr([False, False]) == 0.0
    assert mrr([]) == 0.0


def test_dcg_and_ndcg_hand_computed() -> None:
    # DCG@3 = 1/log2(2) + 1/log2(4) = 1 + 0.5
    assert dcg_at_k(FLAGS, 3) == pytest.approx(1.5)
    # ideal DCG@3 with 4 relevant chunks = 1 + 1/log2(3) + 1/log2(4)
    ideal = 1.0 + 1.0 / math.log2(3) + 0.5
    assert ndcg_at_k(FLAGS, N_RELEVANT, 3) == pytest.approx(1.5 / ideal)
    # Only 1 relevant chunk exists and it is at rank 1: perfect.
    assert ndcg_at_k([True, False], 1, 2) == 1.0
    # Ideal is capped at k: with k=1 the single hit at rank 1 is perfect even if 4 exist.
    assert ndcg_at_k(FLAGS, N_RELEVANT, 1) == 1.0
    assert ndcg_at_k([False, False], 2, 2) == 0.0
    assert ndcg_at_k(FLAGS, 0, 3) == 0.0


def test_ties_and_edge_cases() -> None:
    # A relevant chunk at rank 2 scores 1/log2(3) against an ideal of 1.
    assert ndcg_at_k([False, True], 1, 2) == pytest.approx(1 / math.log2(3))


@pytest.mark.parametrize("bad_k", [0, -1])
def test_non_positive_k_rejected(bad_k: int) -> None:
    with pytest.raises(ValueError, match="positive"):
        recall_at_k(FLAGS, 1, bad_k)
    with pytest.raises(ValueError, match="positive"):
        precision_at_k(FLAGS, bad_k)
    with pytest.raises(ValueError, match="positive"):
        hit_at_k(FLAGS, bad_k)
    with pytest.raises(ValueError, match="positive"):
        ndcg_at_k(FLAGS, 1, bad_k)
