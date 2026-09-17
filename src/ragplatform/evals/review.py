"""Review session logic for ``rag eval review`` (no terminal I/O in here).

A :class:`ReviewSession` loads a candidates file, keeps every decision in a
sidecar ``<candidates>.review.json`` so a review can be quit and resumed, and
appends accepted items to ``eval_sets/<name>/items.jsonl`` with
``created_by="synthetic_reviewed"``. The CLI only handles prompting; every
state transition lives here so it can be unit-tested without input.
"""

from __future__ import annotations

from collections import Counter
from typing import TYPE_CHECKING, Literal

from pydantic import BaseModel, ConfigDict, Field

from ragplatform.evals.candidates import Candidate, read_candidates
from ragplatform.evals.eval_set import ITEMS_FILE, append_item, read_items, write_manifest
from ragplatform.evals.models import Category, Difficulty, EvalItem, SourceRef
from ragplatform.ingestion.dataset import utc_now_iso

if TYPE_CHECKING:
    from pathlib import Path

Action = Literal["accept", "reject"]


class Decision(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    candidate_id: str
    action: Action
    item_id: str | None = None
    decided_at: str


class ReviewState(BaseModel):
    model_config = ConfigDict(extra="forbid")

    candidates_file: str
    decisions: dict[str, Decision] = Field(default_factory=dict)


class ReviewProgress(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    total: int
    accepted: int
    rejected: int
    pending: int
    items_in_set: int
    category_counts: dict[str, int]
    unanswerable_share: float


class ReviewSession:
    def __init__(self, candidates_path: Path, eval_set_dir: Path, eval_set_name: str) -> None:
        self.candidates_path = candidates_path
        self.eval_set_dir = eval_set_dir
        self.eval_set_name = eval_set_name
        self.items_path = eval_set_dir / ITEMS_FILE
        self.state_path = candidates_path.with_suffix(candidates_path.suffix + ".review.json")
        self.candidates = read_candidates(candidates_path)
        self.state = self._load_state()

    # --- persistence ------------------------------------------------------
    def _load_state(self) -> ReviewState:
        if self.state_path.exists():
            state = ReviewState.model_validate_json(self.state_path.read_text(encoding="utf-8"))
            if state.candidates_file != self.candidates_path.name:
                raise ValueError("review state belongs to a different candidates file")
            return state
        return ReviewState(candidates_file=self.candidates_path.name)

    def _save_state(self) -> None:
        self.state_path.write_text(self.state.model_dump_json(indent=2), encoding="utf-8")

    # --- queries ------------------------------------------------------------
    def pending(self) -> list[Candidate]:
        return [c for c in self.candidates if c.id not in self.state.decisions]

    def progress(self) -> ReviewProgress:
        decisions = self.state.decisions.values()
        items = read_items(self.items_path)
        counts = Counter(item.category for item in items)
        n_unanswerable = sum(1 for item in items if not item.answerable)
        return ReviewProgress(
            total=len(self.candidates),
            accepted=sum(1 for d in decisions if d.action == "accept"),
            rejected=sum(1 for d in decisions if d.action == "reject"),
            pending=len(self.pending()),
            items_in_set=len(items),
            category_counts=dict(sorted(counts.items())),
            unanswerable_share=(n_unanswerable / len(items)) if items else 0.0,
        )

    # --- decisions ----------------------------------------------------------
    def accept(
        self,
        candidate: Candidate,
        *,
        question: str | None = None,
        reference_answer: str | None = None,
        category: Category | None = None,
        difficulty: Difficulty | None = None,
        sources: list[SourceRef] | None = None,
        notes: str = "",
    ) -> EvalItem:
        """Accept (optionally edited) and append to the eval set; returns the item."""
        if candidate.id in self.state.decisions:
            raise ValueError(f"candidate {candidate.id} already decided")
        final_category: Category = category or candidate.category
        answerable = final_category != "unanswerable"
        if sources is None:
            sources = (
                [
                    SourceRef(
                        doc_id=candidate.source.doc_id, section_path=candidate.source.section_path
                    )
                ]
                if answerable
                else []
            )
        item = EvalItem(
            id=candidate.id,
            question=question or candidate.question,
            reference_answer=reference_answer or candidate.reference_answer,
            relevant_sources=sources if answerable else [],
            category=final_category,
            difficulty=difficulty or candidate.difficulty,
            answerable=answerable,
            created_by="synthetic_reviewed",
            notes=notes,
        )
        existing_ids = {i.id for i in read_items(self.items_path)}
        if item.id in existing_ids:
            raise ValueError(f"item {item.id} already exists in {self.items_path}")
        append_item(self.items_path, item)
        write_manifest(self.eval_set_dir, self.eval_set_name)
        self.state.decisions[candidate.id] = Decision(
            candidate_id=candidate.id, action="accept", item_id=item.id, decided_at=utc_now_iso()
        )
        self._save_state()
        return item

    def reject(self, candidate: Candidate) -> None:
        if candidate.id in self.state.decisions:
            raise ValueError(f"candidate {candidate.id} already decided")
        self.state.decisions[candidate.id] = Decision(
            candidate_id=candidate.id, action="reject", decided_at=utc_now_iso()
        )
        self._save_state()
