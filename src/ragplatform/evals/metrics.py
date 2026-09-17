"""Retrieval metrics with binary relevance, as pure functions.

Every function takes ``relevance``: the relevance flag of each retrieved chunk
in rank order (rank 1 first). ``n_relevant`` is the total number of relevant
chunks that exist in the corpus for the query (the recall / ideal-DCG
denominator). When ``n_relevant`` is zero the label matched nothing, so the
recall-style metrics return 0.0 and the caller should flag the item.
"""

from __future__ import annotations

import math
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence


def _check_k(k: int) -> None:
    if k <= 0:
        raise ValueError("k must be positive")


def recall_at_k(relevance: Sequence[bool], n_relevant: int, k: int) -> float:
    """Relevant chunks in the top k divided by all relevant chunks in the corpus."""
    _check_k(k)
    if n_relevant <= 0:
        return 0.0
    return min(1.0, sum(relevance[:k]) / n_relevant)


def precision_at_k(relevance: Sequence[bool], k: int) -> float:
    """Relevant chunks in the top k divided by k (missing ranks count as irrelevant)."""
    _check_k(k)
    return sum(relevance[:k]) / k


def hit_at_k(relevance: Sequence[bool], k: int) -> float:
    """1.0 when at least one relevant chunk is in the top k, else 0.0."""
    _check_k(k)
    return 1.0 if any(relevance[:k]) else 0.0


def mrr(relevance: Sequence[bool]) -> float:
    """1 / rank of the first relevant chunk; 0.0 when none is retrieved."""
    for rank, relevant in enumerate(relevance, start=1):
        if relevant:
            return 1.0 / rank
    return 0.0


def dcg_at_k(relevance: Sequence[bool], k: int) -> float:
    """Binary-gain DCG: sum of 1 / log2(rank + 1) over relevant ranks <= k."""
    _check_k(k)
    return sum(1.0 / math.log2(rank + 1) for rank, rel in enumerate(relevance[:k], start=1) if rel)


def ndcg_at_k(relevance: Sequence[bool], n_relevant: int, k: int) -> float:
    """DCG@k divided by the ideal DCG of ``min(n_relevant, k)`` relevant chunks ranked first."""
    _check_k(k)
    ideal_hits = min(n_relevant, k)
    if ideal_hits <= 0:
        return 0.0
    ideal = dcg_at_k([True] * ideal_hits, k)
    return dcg_at_k(relevance, k) / ideal
