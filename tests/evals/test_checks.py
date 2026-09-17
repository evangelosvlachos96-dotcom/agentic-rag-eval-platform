"""Tests for the programmatic generation checks."""

from __future__ import annotations

from ragplatform.evals.checks import programmatic_checks
from ragplatform.evals.models import EvalItem, SourceRef
from ragplatform.models import Answer, Citation

ANSWERABLE = EvalItem(
    id="a",
    question="q?",
    reference_answer="r",
    relevant_sources=[SourceRef(doc_id="d")],
    category="lookup",
    created_by="human",
)
UNANSWERABLE = EvalItem(
    id="u",
    question="q?",
    reference_answer="The corpus does not contain this information.",
    category="unanswerable",
    answerable=False,
    created_by="human",
)


def test_answered_with_valid_citations() -> None:
    answer = Answer(query="q?", text="yes", citations=[Citation(chunk_id="c1")])
    checks = programmatic_checks(answer, ANSWERABLE)
    assert checks.citations_valid is True
    assert checks.n_citations == 1
    assert checks.answered_without_citations is False
    assert checks.unnecessary_abstention is False
    assert checks.missed_abstention is False
    assert checks.correct_abstention is False


def test_invalid_and_missing_citations_are_flagged() -> None:
    answer = Answer(query="q?", text="yes", citations=[], invalid_citations=["zzz"])
    checks = programmatic_checks(answer, ANSWERABLE)
    assert checks.citations_valid is False
    assert checks.n_invalid_citations == 1
    assert checks.answered_without_citations is True


def test_abstention_cases() -> None:
    abstained = Answer(query="q?", text="", abstained=True)
    answered = Answer(query="q?", text="42", citations=[Citation(chunk_id="c")])
    assert programmatic_checks(abstained, UNANSWERABLE).correct_abstention is True
    assert programmatic_checks(abstained, UNANSWERABLE).missed_abstention is False
    assert programmatic_checks(answered, UNANSWERABLE).missed_abstention is True
    assert programmatic_checks(answered, UNANSWERABLE).correct_abstention is False
    assert programmatic_checks(abstained, ANSWERABLE).unnecessary_abstention is True
    assert programmatic_checks(abstained, ANSWERABLE).answered_without_citations is False
