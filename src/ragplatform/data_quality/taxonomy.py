"""Observable failure signals; source-label misses are not semantic judgments."""

from __future__ import annotations

from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from ragplatform.evals.results import ItemResult

Failure = Literal[
    "execution_error",
    "unmatched_labels",
    "labeled_retrieval_miss",
    "invalid_citation",
    "uncited_answer",
    "missed_abstention",
    "unnecessary_abstention",
    "judge_incorrect",
    "judge_unsupported",
]


def classify(result: ItemResult) -> list[Failure]:
    failures: list[Failure] = []
    if result.error:
        failures.append("execution_error")
    if result.answerable and result.retrieval is not None:
        if not result.retrieval.labels_matched:
            failures.append("unmatched_labels")
        elif not any(r.relevant for r in result.retrieval.retrieved):
            failures.append("labeled_retrieval_miss")
    if result.checks:
        checks = result.checks
        if not checks.citations_valid:
            failures.append("invalid_citation")
        if checks.answered_without_citations:
            failures.append("uncited_answer")
        if checks.missed_abstention:
            failures.append("missed_abstention")
        if checks.unnecessary_abstention:
            failures.append("unnecessary_abstention")
    if result.judges:
        if result.judges.correctness and not result.judges.correctness.correct:
            failures.append("judge_incorrect")
        if result.judges.faithfulness:
            score = result.judges.faithfulness.score
            if score is not None and score < 1:
                failures.append("judge_unsupported")
    return failures
