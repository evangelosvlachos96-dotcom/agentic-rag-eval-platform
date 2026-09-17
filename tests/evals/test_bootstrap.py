"""Tests for ragplatform.evals.bootstrap."""

from __future__ import annotations

import pytest

from ragplatform.evals.bootstrap import bootstrap_ci, paired_bootstrap


def test_bootstrap_is_reproducible_with_a_seed() -> None:
    values = [0.12, 0.8, 0.55, 0.9, 0.3, 0.71, 0.66, 0.05, 0.98, 0.43]
    a = bootstrap_ci(values, n_resamples=500, seed=42)
    b = bootstrap_ci(values, n_resamples=500, seed=42)
    assert a == b
    assert a.mean == pytest.approx(sum(values) / len(values))
    assert a.lower < a.mean < a.upper
    assert a.lower >= min(values)
    assert a.upper <= max(values)
    assert a.n == 10
    assert a.confidence == 0.95


def test_bootstrap_of_constant_sample_has_zero_width() -> None:
    ci = bootstrap_ci([0.5] * 8, n_resamples=100, seed=0)
    assert ci.lower == ci.upper == ci.mean == 0.5


def test_bootstrap_rejects_bad_input() -> None:
    with pytest.raises(ValueError, match="empty"):
        bootstrap_ci([])
    with pytest.raises(ValueError, match="n_resamples"):
        bootstrap_ci([1.0], n_resamples=0)
    with pytest.raises(ValueError, match="confidence"):
        bootstrap_ci([1.0], confidence=1.5)


def test_paired_bootstrap_toy_example() -> None:
    # B beats A on every item by exactly 0.1: the delta is constant and clearly non-zero.
    a = [0.5, 0.6, 0.7, 0.8, 0.4, 0.6]
    b = [x + 0.1 for x in a]
    result = paired_bootstrap(a, b, n_resamples=200, seed=1)
    assert result.delta == pytest.approx(0.1)
    assert result.lower == pytest.approx(0.1)
    assert result.upper == pytest.approx(0.1)
    assert result.distinguishable is True
    assert result.mean_b > result.mean_a
    assert result.n == 6


def test_paired_bootstrap_noise_is_not_distinguishable() -> None:
    a = [1.0, 0.0, 1.0, 0.0, 1.0, 0.0, 1.0, 0.0]
    b = [0.0, 1.0, 1.0, 0.0, 1.0, 0.0, 0.0, 1.0]  # same mean, items shuffled
    result = paired_bootstrap(a, b, n_resamples=500, seed=3)
    assert result.delta == pytest.approx(0.0)
    assert result.lower < 0.0 < result.upper
    assert result.distinguishable is False


def test_paired_bootstrap_rejects_mismatched_lengths() -> None:
    with pytest.raises(ValueError, match="same length"):
        paired_bootstrap([1.0], [1.0, 2.0])
    with pytest.raises(ValueError, match="empty"):
        paired_bootstrap([], [])
