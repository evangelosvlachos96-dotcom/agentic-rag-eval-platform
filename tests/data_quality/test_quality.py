"""Hand-checkable agreement and annotation integrity tests."""

import pytest

from ragplatform.data_quality.agreement import agreement
from ragplatform.data_quality.annotations import (
    Annotation,
    AnnotationBatch,
    compare_annotations,
    duplicate_questions,
    import_batch,
)
from ragplatform.data_quality.taxonomy import classify
from ragplatform.evals.results import ItemResult, RetrievalEvaluation


def batch() -> AnnotationBatch:
    return AnnotationBatch(
        run_id="run",
        results_sha256="hash",
        dataset_version="data",
        eval_set_version="eval",
        rows=[
            Annotation(
                item_id="a",
                question="q",
                reference_answer="ref",
                answer="answer",
                evidence={"chunk": "text"},
            )
        ],
    )


def test_agreement_known_values_and_undefined() -> None:
    score = agreement(
        dict(zip("abcd", "0011", strict=True)), dict(zip("abcd", "0001", strict=True))
    )
    assert score.observed == 0.75
    assert score.expected == 0.5
    assert score.kappa == 0.5
    assert agreement({"a": "yes"}, {"a": "yes"}).kappa is None
    assert agreement({}, {}).observed is None
    partial = agreement({"a": "yes", "b": "no"}, {"a": "no", "c": "yes"})
    assert partial.paired == 1
    assert partial.missing_left == partial.missing_right == 1


def test_import_preserves_evidence_and_provenance() -> None:
    original = batch()
    labeled = original.model_copy(
        update={
            "reviewer": "test human",
            "reviewer_kind": "human",
            "rows": [original.rows[0].model_copy(update={"verdict": "correct"})],
        }
    )
    assert import_batch(original, labeled) == labeled
    assert original.rows[0].verdict is None
    changes: tuple[dict[str, object], ...] = (
        {"run_id": "different"},
        {"reviewer": ""},
        {"rows": []},
        {"rows": labeled.rows * 2},
    )
    for change in changes:
        with pytest.raises(ValueError, match=r"mismatch|identity|IDs"):
            import_batch(original, labeled.model_copy(update=change))
    tampered = labeled.rows[0].model_copy(update={"evidence": {"chunk": "different"}})
    with pytest.raises(ValueError, match="changed"):
        import_batch(original, labeled.model_copy(update={"rows": [tampered]}))
    assert compare_annotations(original, labeled).paired == 0
    with pytest.raises(ValueError, match="different runs"):
        compare_annotations(original, labeled.model_copy(update={"eval_set_version": "v2"}))


def test_no_correctness_label_without_answer() -> None:
    original = batch()
    row = original.rows[0].model_copy(update={"answer": None})
    original = original.model_copy(update={"rows": [row]})
    labeled = original.model_copy(
        update={
            "reviewer": "human",
            "reviewer_kind": "human",
            "rows": [row.model_copy(update={"verdict": "correct"})],
        }
    )
    with pytest.raises(ValueError, match="without a generated answer"):
        import_batch(original, labeled)


def test_taxonomy_keeps_label_failures_distinct() -> None:
    result = ItemResult(
        item_id="a",
        question="q",
        category="lookup",
        difficulty="easy",
        answerable=True,
        reference_answer="r",
        retrieval=RetrievalEvaluation(
            retrieved=[], n_relevant_in_corpus=2, labels_matched=True, metrics={}
        ),
    )
    assert classify(result) == ["labeled_retrieval_miss"]
    assert classify(
        result.model_copy(
            update={
                "retrieval": result.retrieval.model_copy(update={"labels_matched": False})
                if result.retrieval
                else None
            }
        )
    ) == ["unmatched_labels"]


def test_conservative_duplicates() -> None:
    assert duplicate_questions({"a": "Hello  world", "b": "HELLO world", "c": "Other"}) == [
        ["a", "b"]
    ]


def test_judge_agreement_excludes_uncertain_and_requires_human() -> None:
    from ragplatform.data_quality.annotations import judge_agreement
    from ragplatform.evals.judges import CorrectnessVerdict
    from ragplatform.evals.results import JudgeEvaluation

    original = batch()
    reviewed = original.model_copy(
        update={
            "reviewer": "test",
            "reviewer_kind": "human",
            "rows": [original.rows[0].model_copy(update={"verdict": "correct"})],
        }
    )
    result = ItemResult(
        item_id="a",
        question="q",
        category="lookup",
        difficulty="easy",
        answerable=True,
        reference_answer="r",
        judges=JudgeEvaluation(
            correctness=CorrectnessVerdict(evidence="e", reasoning="r", correct=True)
        ),
    )
    assert judge_agreement(reviewed, [result]).observed == 1
    with pytest.raises(ValueError, match="human reviewer"):
        judge_agreement(original, [result])
    uncertain = reviewed.model_copy(
        update={"rows": [reviewed.rows[0].model_copy(update={"verdict": "uncertain"})]}
    )
    assert judge_agreement(uncertain, [result]).paired == 0
