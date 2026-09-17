"""Reciprocal Rank Fusion (RRF).

Given several ranked lists of ids, each id scores ``sum(1 / (k + rank))`` over
the lists it appears in (rank is 1-based). ``k=60`` is the value from the
original paper (Cormack et al., 2009); it damps the advantage of being first
in a single list so that agreement between lists matters more than any one
list's top hit. RRF needs no score calibration between BM25 and cosine, which
is why it is the default fusion for hybrid search here.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence


def reciprocal_rank_fusion(
    rankings: Sequence[Sequence[str]], k: int = 60
) -> list[tuple[str, float]]:
    """Fuse ranked id lists into one list of ``(id, rrf_score)``, best first.

    Ties are broken by id so the output is deterministic.
    """
    if k <= 0:
        raise ValueError("k must be positive")
    scores: dict[str, float] = {}
    for ranking in rankings:
        for rank, item in enumerate(ranking, start=1):
            scores[item] = scores.get(item, 0.0) + 1.0 / (k + rank)
    return sorted(scores.items(), key=lambda pair: (-pair[1], pair[0]))
