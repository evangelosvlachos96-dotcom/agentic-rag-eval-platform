"""Agreement statistics with explicit missingness and undefined kappa."""

from __future__ import annotations

from collections import Counter
from typing import TYPE_CHECKING

from pydantic import BaseModel, ConfigDict

if TYPE_CHECKING:
    from collections.abc import Mapping


class Agreement(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    paired: int
    missing_left: int
    missing_right: int
    observed: float | None
    expected: float | None
    kappa: float | None


def agreement(left: Mapping[str, str], right: Mapping[str, str]) -> Agreement:
    """Unweighted Cohen's kappa on shared IDs, never treating missing as a label."""
    keys = sorted(left.keys() & right.keys())
    n = len(keys)
    observed = sum(left[k] == right[k] for k in keys) / n if n else None
    a, b = Counter(left[k] for k in keys), Counter(right[k] for k in keys)
    expected = sum(a[v] * b[v] for v in a.keys() | b.keys()) / (n * n) if n else None
    kappa = None
    if observed is not None and expected is not None and expected < 1:
        kappa = (observed - expected) / (1 - expected)
    return Agreement(
        paired=n,
        missing_left=len(right.keys() - left.keys()),
        missing_right=len(left.keys() - right.keys()),
        observed=observed,
        expected=expected,
        kappa=kappa,
    )
