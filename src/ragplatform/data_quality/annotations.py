"""Blank annotation export and validated import, separate from approved eval items."""

from __future__ import annotations

import hashlib
from typing import TYPE_CHECKING, Literal

from pydantic import BaseModel, ConfigDict

from ragplatform.data_quality.agreement import Agreement, agreement

if TYPE_CHECKING:
    from pathlib import Path

    from ragplatform.evals.results import ItemResult
    from ragplatform.models import Chunk


class Annotation(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    item_id: str
    question: str
    reference_answer: str
    answer: str | None
    evidence: dict[str, str]
    verdict: Literal["correct", "incorrect", "uncertain"] | None = None
    notes: str = ""


class AnnotationBatch(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    run_id: str
    results_sha256: str
    dataset_version: str
    eval_set_version: str
    reviewer: str = ""
    reviewer_kind: Literal["human", "assistant", "judge"] | None = None
    rows: list[Annotation]


def export_batch(run_dir: Path, chunks: list[Chunk]) -> AnnotationBatch:
    from ragplatform.evals.results import read_results, read_summary

    summary = read_summary(run_dir)
    results = read_results(run_dir)
    corpus = {c.id: c for c in chunks}
    if len({r.item_id for r in results}) != len(results):
        raise ValueError("Duplicate result IDs")
    rows = []
    for result in results:
        ids = [r.chunk_id for r in result.retrieval.retrieved] if result.retrieval else []
        rows.append(
            Annotation(
                item_id=result.item_id,
                question=result.question,
                reference_answer=result.reference_answer,
                answer=result.answer.text if result.answer else None,
                evidence={key: corpus[key].content for key in ids},
            )
        )
    return AnnotationBatch(
        run_id=summary.run_id,
        results_sha256=hashlib.sha256((run_dir / "results.jsonl").read_bytes()).hexdigest(),
        dataset_version=summary.dataset_version,
        eval_set_version=summary.eval_set_version,
        rows=rows,
    )


def import_batch(original: AnnotationBatch, reviewed: AnnotationBatch) -> AnnotationBatch:
    """Validate identity and unchanged evidence. Never writes to the eval set."""
    if not reviewed.reviewer.strip() or reviewed.reviewer_kind is None:
        raise ValueError("Reviewer identity and kind are required")
    fields = {"run_id", "results_sha256", "dataset_version", "eval_set_version"}
    if original.model_dump(include=fields) != reviewed.model_dump(include=fields):
        raise ValueError("Annotation provenance mismatch")
    source = {r.item_id: r for r in original.rows}
    if len(source) != len(original.rows) or len({r.item_id for r in reviewed.rows}) != len(
        reviewed.rows
    ):
        raise ValueError("Duplicate annotation IDs")
    if source.keys() != {r.item_id for r in reviewed.rows}:
        raise ValueError("Annotation item IDs differ")
    for row in reviewed.rows:
        if row.model_dump(exclude={"verdict", "notes"}) != source[row.item_id].model_dump(
            exclude={"verdict", "notes"}
        ):
            raise ValueError("Question, answer or evidence was changed")
        if row.verdict is not None and row.answer is None:
            raise ValueError("Cannot judge answer correctness without a generated answer")
    return reviewed


def compare_annotations(left: AnnotationBatch, right: AnnotationBatch) -> Agreement:
    fields = {"run_id", "results_sha256", "dataset_version", "eval_set_version"}
    if left.model_dump(include=fields) != right.model_dump(include=fields):
        raise ValueError("Cannot compare different runs")
    for batch in (left, right):
        if len({r.item_id for r in batch.rows}) != len(batch.rows):
            raise ValueError("Duplicate annotation IDs")
    return agreement(
        {r.item_id: r.verdict for r in left.rows if r.verdict is not None},
        {r.item_id: r.verdict for r in right.rows if r.verdict is not None},
    )


def judge_agreement(reviewed: AnnotationBatch, results: list[ItemResult]) -> Agreement:
    """Compare binary human correctness with stored judge verdicts; exclude uncertain."""
    if reviewed.reviewer_kind != "human":
        raise ValueError("Judge-human agreement requires a human reviewer")
    if len({r.item_id for r in results}) != len(results):
        raise ValueError("Duplicate result IDs")
    human = {r.item_id: r.verdict for r in reviewed.rows if r.verdict in {"correct", "incorrect"}}
    judges = {
        r.item_id: "correct" if r.judges.correctness.correct else "incorrect"
        for r in results
        if r.judges is not None and r.judges.correctness is not None
    }
    return agreement(human, judges)


def save_batch(path: Path, batch: AnnotationBatch) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as handle:
        handle.write(batch.model_dump_json(indent=2) + "\n")


def duplicate_questions(questions: dict[str, str]) -> list[list[str]]:
    """Conservative exact duplicate groups after Unicode/case/whitespace normalization."""
    import unicodedata

    groups: dict[str, list[str]] = {}
    for key, question in questions.items():
        normalized = " ".join(unicodedata.normalize("NFKC", question).casefold().split())
        groups.setdefault(normalized, []).append(key)
    return [ids for ids in groups.values() if len(ids) > 1]
