"""Offline sensitivity checks for proposed exact-section relevance additions.

These diagnostics never modify approved labels or saved retrieval results.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Literal

from pydantic import BaseModel, ConfigDict, Field

from ragplatform.evals.metrics import hit_at_k, mrr

if TYPE_CHECKING:
    from ragplatform.evals.results import ItemResult


class ProposedSource(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    item_id: str
    doc_id: str
    section_path: str = Field(min_length=1)
    evidence: str = Field(min_length=1)
    rationale: str = Field(min_length=1)
    status: Literal["assistant_proposed"] = "assistant_proposed"


class SensitivityResult(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    item_id: str
    original: dict[str, float]
    proposed: dict[str, float]
    newly_relevant_chunks: list[str]


def rescore_saved(
    results: list[ItemResult], proposals: list[ProposedSource], *, k: int = 8
) -> list[SensitivityResult]:
    """Compare hit/MRR only; exact matching avoids expanding to child sections.

    Additional alternatives do not define exhaustive relevance or required facts,
    so recall, nDCG and complete-source coverage are deliberately not inferred.
    """
    if k < 1:
        raise ValueError("k must be positive")
    items = {r.item_id: r for r in results}
    if len(items) != len(results):
        raise ValueError("Duplicate result item IDs")
    keys = [(p.item_id, p.doc_id, p.section_path) for p in proposals]
    if len(set(keys)) != len(keys):
        raise ValueError("Duplicate proposed sources")
    for proposal in proposals:
        if proposal.item_id not in items or not items[proposal.item_id].answerable:
            raise ValueError("Proposals must refer to known answerable items")
    output: list[SensitivityResult] = []
    for result in results:
        if result.error or result.retrieval is None:
            raise ValueError("Complete successful retrieval results required")
        ranked = result.retrieval.retrieved
        if [r.rank for r in ranked] != list(range(1, len(ranked) + 1)):
            raise ValueError("Saved ranks must be contiguous and ordered")
        if len({r.chunk_id for r in ranked}) != len(ranked):
            raise ValueError("Duplicate retrieved chunks")
        if not result.answerable:
            continue
        sources = {(p.doc_id, p.section_path) for p in proposals if p.item_id == result.item_id}
        before = [r.relevant for r in ranked[:k]]
        after = [r.relevant or (r.doc_id, r.section_path) in sources for r in ranked[:k]]
        output.append(
            SensitivityResult(
                item_id=result.item_id,
                original={
                    "hit@1": hit_at_k(before, 1),
                    f"hit@{k}": hit_at_k(before, k),
                    "mrr": mrr(before),
                },
                proposed={
                    "hit@1": hit_at_k(after, 1),
                    f"hit@{k}": hit_at_k(after, k),
                    "mrr": mrr(after),
                },
                newly_relevant_chunks=[
                    r.chunk_id
                    for r, old, new in zip(ranked, before, after, strict=False)
                    if new and not old
                ],
            )
        )
    return output
