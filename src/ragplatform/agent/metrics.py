"""Finite-sample success estimators for repeated independent attempts."""

from math import comb


def pass_at_k(n: int, successes: int, k: int) -> float:
    """Probability at least one of k draws without replacement succeeds."""
    _validate(n, successes, k)
    return 1.0 - (comb(n - successes, k) / comb(n, k) if n - successes >= k else 0.0)


def pass_power_k(n: int, successes: int, k: int) -> float:
    """Probability all k draws without replacement succeed; consistency estimate."""
    _validate(n, successes, k)
    return comb(successes, k) / comb(n, k) if successes >= k else 0.0


def _validate(n: int, successes: int, k: int) -> None:
    if not 0 <= successes <= n or not 1 <= k <= n:
        raise ValueError("Require 0 <= successes <= n and 1 <= k <= n")
