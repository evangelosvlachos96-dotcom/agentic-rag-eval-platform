"""Offline checks before publishing a reviewed evaluation baseline."""

from __future__ import annotations

from collections import Counter
from typing import TYPE_CHECKING

from pydantic import BaseModel, ConfigDict

from ragplatform.evals.models import CATEGORIES
from ragplatform.evals.relevance import count_relevant_chunks

if TYPE_CHECKING:
    from collections.abc import Sequence

    from ragplatform.evals.models import EvalItem
    from ragplatform.models import Chunk


class ReadinessReport(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    n_items: int
    category_counts: dict[str, int]
    errors: list[str]
    warnings: list[str]

    @property
    def ready(self) -> bool:
        return not self.errors


def audit_eval_set(items: Sequence[EvalItem], chunks: Sequence[Chunk]) -> ReadinessReport:
    """Validate every source separately; these checks cannot replace human review."""
    errors: list[str] = []
    warnings: list[str] = []
    if not items:
        errors.append("The evaluation set is empty.")
    ids = Counter(item.id for item in items)
    for item_id, count in ids.items():
        if count > 1:
            errors.append(f"Duplicate item id: {item_id}")
    questions = Counter(" ".join(item.question.casefold().split()) for item in items)
    if any(count > 1 for count in questions.values()):
        errors.append("Duplicate questions after whitespace/case normalization.")
    counts: Counter[str] = Counter(item.category for item in items)
    for category in CATEGORIES:
        if not counts[category]:
            warnings.append(f"No items in category {category}.")
    if len(items) < 60:
        warnings.append("Fewer than 60 items: treat this as a pilot, not a full benchmark.")
    for item in items:
        matched = count_relevant_chunks(chunks, item.relevant_sources)
        for source in item.relevant_sources:
            if count_relevant_chunks(chunks, [source]) == 0:
                # Ordinary labels can list alternative passages removed by deduplication.
                # Multi-source tasks need every labeled source checked before a baseline.
                findings = (
                    errors
                    if not matched or item.category in {"multi_hop", "comparison"}
                    else warnings
                )
                findings.append(
                    f"{item.id}: unmatched source {source.doc_id} > {source.section_path}"
                )
        if not item.answerable and item.relevant_sources:
            errors.append(f"{item.id}: unanswerable item must not have relevant sources.")
        if item.category in {"multi_hop", "comparison"} and len(item.relevant_sources) < 2:
            warnings.append(f"{item.id}: verify that this question has all required sources.")
    return ReadinessReport(
        n_items=len(items),
        category_counts=dict(sorted(counts.items())),
        errors=errors,
        warnings=warnings,
    )
