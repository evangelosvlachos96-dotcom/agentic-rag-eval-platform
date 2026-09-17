"""Tests for the review session logic (accept, edit, reject, resume) without a terminal."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from ragplatform.evals.candidates import Candidate, CandidateSource, write_candidates
from ragplatform.evals.eval_set import read_items
from ragplatform.evals.models import SourceRef
from ragplatform.evals.review import ReviewSession

if TYPE_CHECKING:
    from pathlib import Path


def _candidate(i: int, category: str = "lookup") -> Candidate:
    answerable = category != "unanswerable"
    return Candidate(
        id=f"cand-t-{i:04d}",
        question=f"Question {i}?",
        reference_answer="Answer."
        if answerable
        else "The corpus does not contain this information.",
        category=category,  # type: ignore[arg-type]  # test helper takes plain strings
        difficulty="easy",
        answerable=answerable,
        target_category=category,
        source=CandidateSource(
            chunk_id=f"doc-{i:04d}",
            doc_id="doc",
            doc_title="Doc",
            section_path="Spec > A",
            text="t",
        ),
        model="fake-model",
        prompt_version="generate_candidates_v1",
        created_at="2026-01-01T00:00:00+00:00",
    )


@pytest.fixture
def session(tmp_path: Path) -> ReviewSession:
    candidates_path = tmp_path / "candidates" / "batch.jsonl"
    write_candidates(candidates_path, [_candidate(0), _candidate(1, "unanswerable"), _candidate(2)])
    return ReviewSession(candidates_path, tmp_path / "eval_sets" / "v1", "v1")


def test_accept_appends_item_with_default_source(session: ReviewSession) -> None:
    item = session.accept(session.pending()[0])
    assert item.id == "cand-t-0000"
    assert item.created_by == "synthetic_reviewed"
    assert item.relevant_sources == [SourceRef(doc_id="doc", section_path="Spec > A")]
    assert read_items(session.items_path) == [item]
    assert (session.eval_set_dir / "manifest.json").exists()
    progress = session.progress()
    assert (progress.accepted, progress.rejected, progress.pending) == (1, 0, 2)
    assert progress.category_counts == {"lookup": 1}


def test_accept_with_edits_overrides_fields(session: ReviewSession) -> None:
    candidate = session.pending()[0]
    item = session.accept(
        candidate,
        question="Edited?",
        reference_answer="Edited answer.",
        category="exact_term",
        difficulty="hard",
        sources=[SourceRef(doc_id="doc", section_path="Spec"), SourceRef(doc_id="other")],
        notes="reviewer note",
    )
    assert item.question == "Edited?"
    assert item.category == "exact_term"
    assert item.difficulty == "hard"
    assert [s.doc_id for s in item.relevant_sources] == ["doc", "other"]
    assert item.notes == "reviewer note"


def test_unanswerable_accept_has_no_sources(session: ReviewSession) -> None:
    item = session.accept(session.pending()[1])
    assert item.answerable is False
    assert item.relevant_sources == []
    assert session.progress().unanswerable_share == 1.0


def test_changing_category_to_unanswerable_drops_sources(session: ReviewSession) -> None:
    item = session.accept(session.pending()[0], category="unanswerable")
    assert item.answerable is False
    assert item.relevant_sources == []


def test_reject_records_decision_without_item(session: ReviewSession) -> None:
    session.reject(session.pending()[0])
    assert read_items(session.items_path) == []
    assert session.progress().rejected == 1
    assert [c.id for c in session.pending()] == ["cand-t-0001", "cand-t-0002"]


def test_resume_reloads_decisions_from_disk(session: ReviewSession) -> None:
    session.accept(session.pending()[0])
    session.reject(session.pending()[0])
    resumed = ReviewSession(session.candidates_path, session.eval_set_dir, "v1")
    assert [c.id for c in resumed.pending()] == ["cand-t-0002"]
    progress = resumed.progress()
    assert (progress.accepted, progress.rejected, progress.pending) == (1, 1, 1)


def test_double_decision_is_rejected(session: ReviewSession) -> None:
    candidate = session.pending()[0]
    session.accept(candidate)
    with pytest.raises(ValueError, match="already decided"):
        session.reject(candidate)
    with pytest.raises(ValueError, match="already decided"):
        session.accept(candidate)


def test_state_file_must_match_candidates_file(session: ReviewSession, tmp_path: Path) -> None:
    session.accept(session.pending()[0])
    other = tmp_path / "candidates" / "other.jsonl"
    write_candidates(other, [_candidate(9)])
    other.with_suffix(".jsonl.review.json").write_text(
        session.state_path.read_text(encoding="utf-8"), encoding="utf-8"
    )
    with pytest.raises(ValueError, match="different candidates file"):
        ReviewSession(other, session.eval_set_dir, "v1")
