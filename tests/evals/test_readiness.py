"""Readiness catches label drift even when another label still matches."""

from ragplatform.evals.models import EvalItem, SourceRef
from ragplatform.evals.readiness import audit_eval_set
from ragplatform.models import Chunk


def test_checks_every_source_and_duplicate_question() -> None:
    chunk = Chunk(
        id="c",
        document_id="d",
        content="text",
        index=0,
        metadata={
            "section_path": "Spec",
            "doc_title": "Doc",
            "char_start": 0,
            "char_end": 4,
            "token_count": 1,
        },
    )
    item = EvalItem(
        id="i",
        question="A question?",
        reference_answer="Answer",
        relevant_sources=[SourceRef(doc_id="d", section_path="Spec"), SourceRef(doc_id="missing")],
        category="multi_hop",
        created_by="human",
    )
    report = audit_eval_set([item], [chunk])
    assert not report.ready
    assert len(report.errors) == 1
    assert "missing" in report.errors[0]
    fixed = item.model_copy(update={"relevant_sources": [SourceRef(doc_id="d")]})
    assert audit_eval_set([fixed], [chunk]).ready
    duplicate = fixed.model_copy(update={"id": "other", "question": " A  QUESTION? "})
    assert not audit_eval_set([fixed, duplicate], [chunk]).ready
    assert not audit_eval_set([], [chunk]).ready


def test_small_set_is_marked_as_pilot() -> None:
    item = EvalItem(
        id="u",
        question="Unknown?",
        reference_answer="Not in corpus",
        category="unanswerable",
        answerable=False,
        created_by="human",
    )
    report = audit_eval_set([item], [])
    assert report.ready
    assert any("pilot" in warning for warning in report.warnings)
