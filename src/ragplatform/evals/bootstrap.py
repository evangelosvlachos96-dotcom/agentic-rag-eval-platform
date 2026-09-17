"""Bootstrap confidence intervals, seeded for reproducibility.

``bootstrap_ci`` resamples the per-item values with replacement ``n_resamples``
times, computes the mean of each resample, and reports the percentile interval
(2.5% and 97.5% for a 95% CI). ``paired_bootstrap`` compares two runs on the
*same* items: it resamples item indices and recomputes the mean difference, so
item-level variance that both runs share cancels out. A difference is called
distinguishable from noise when the interval excludes zero.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
from pydantic import BaseModel, ConfigDict, Field

if TYPE_CHECKING:
    from collections.abc import Sequence


class ConfidenceInterval(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    mean: float
    lower: float
    upper: float
    n: int = Field(ge=1)
    confidence: float
    n_resamples: int
    seed: int


class PairedComparison(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    mean_a: float
    mean_b: float
    delta: float = Field(description="mean_b - mean_a")
    lower: float
    upper: float
    n: int = Field(ge=1)
    confidence: float
    n_resamples: int
    seed: int
    distinguishable: bool = Field(description="True when the CI excludes zero.")


def _percentiles(confidence: float) -> tuple[float, float]:
    if not 0.0 < confidence < 1.0:
        raise ValueError("confidence must be in (0, 1)")
    alpha = (1.0 - confidence) / 2.0
    return 100.0 * alpha, 100.0 * (1.0 - alpha)


def bootstrap_ci(
    values: Sequence[float],
    n_resamples: int = 1000,
    seed: int = 0,
    confidence: float = 0.95,
) -> ConfidenceInterval:
    if not values:
        raise ValueError("cannot bootstrap an empty sample")
    if n_resamples <= 0:
        raise ValueError("n_resamples must be positive")
    lo_pct, hi_pct = _percentiles(confidence)
    data = np.asarray(values, dtype=np.float64)
    rng = np.random.default_rng(seed)
    indices = rng.integers(0, len(data), size=(n_resamples, len(data)))
    means = data[indices].mean(axis=1)
    return ConfidenceInterval(
        mean=float(data.mean()),
        lower=float(np.percentile(means, lo_pct)),
        upper=float(np.percentile(means, hi_pct)),
        n=len(data),
        confidence=confidence,
        n_resamples=n_resamples,
        seed=seed,
    )


def paired_bootstrap(
    a: Sequence[float],
    b: Sequence[float],
    n_resamples: int = 1000,
    seed: int = 0,
    confidence: float = 0.95,
) -> PairedComparison:
    """CI for ``mean(b) - mean(a)`` where ``a[i]`` and ``b[i]`` score the same item."""
    if len(a) != len(b):
        raise ValueError("paired samples must have the same length")
    if not a:
        raise ValueError("cannot bootstrap an empty sample")
    if n_resamples <= 0:
        raise ValueError("n_resamples must be positive")
    lo_pct, hi_pct = _percentiles(confidence)
    diffs = np.asarray(b, dtype=np.float64) - np.asarray(a, dtype=np.float64)
    rng = np.random.default_rng(seed)
    indices = rng.integers(0, len(diffs), size=(n_resamples, len(diffs)))
    means = diffs[indices].mean(axis=1)
    lower = float(np.percentile(means, lo_pct))
    upper = float(np.percentile(means, hi_pct))
    return PairedComparison(
        mean_a=float(np.mean(a)),
        mean_b=float(np.mean(b)),
        delta=float(diffs.mean()),
        lower=lower,
        upper=upper,
        n=len(diffs),
        confidence=confidence,
        n_resamples=n_resamples,
        seed=seed,
        distinguishable=lower > 0.0 or upper < 0.0,
    )
