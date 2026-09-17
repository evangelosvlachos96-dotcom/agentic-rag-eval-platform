"""Per-item results and the run summary written by ``rag eval run``.

Run directory layout (``experiments/runs/<timestamp>_<config>/``):

- ``config.json``    snapshot of the :class:`RunConfig`
- ``results.jsonl``  one :class:`ItemResult` per eval item
- ``summary.json``   :class:`RunSummary`: provenance, metrics with CIs, cost
- ``report.md``      human-readable report
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import BaseModel, ConfigDict, Field

from ragplatform.evals.checks import ProgrammaticChecks
from ragplatform.evals.judges import CorrectnessVerdict, FaithfulnessVerdict, RelevanceVerdict
from ragplatform.models import Answer, TokenUsage

if TYPE_CHECKING:
    from pathlib import Path

CONFIG_FILE = "config.json"
RESULTS_FILE = "results.jsonl"
SUMMARY_FILE = "summary.json"
REPORT_FILE = "report.md"


class RetrievedSummary(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    chunk_id: str
    doc_id: str
    doc_title: str
    section_path: str
    rank: int
    score: float
    relevant: bool


class RetrievalEvaluation(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    retrieved: list[RetrievedSummary]
    n_relevant_in_corpus: int = Field(ge=0)
    labels_matched: bool = Field(
        description="False when no chunk in the corpus matches the labels."
    )
    metrics: dict[str, float]


class JudgeEvaluation(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    faithfulness: FaithfulnessVerdict | None = None
    correctness: CorrectnessVerdict | None = None
    relevance: RelevanceVerdict | None = None
    usage: TokenUsage = Field(default_factory=lambda: TokenUsage(input_tokens=0, output_tokens=0))


class ItemResult(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    item_id: str
    question: str
    category: str
    difficulty: str
    answerable: bool
    reference_answer: str
    retrieval: RetrievalEvaluation | None = None
    answer: Answer | None = None
    checks: ProgrammaticChecks | None = None
    judges: JudgeEvaluation | None = None
    error: str | None = None
    metrics: dict[str, float] = Field(
        default_factory=dict, description="Flat per-item metric values used for aggregation."
    )


class MetricSummary(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    mean: float
    ci_lower: float
    ci_upper: float
    n: int


class RunSummary(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    run_id: str
    config_name: str
    created_at: str
    git_commit: str | None
    git_dirty: bool | None
    dataset_version: str
    eval_set_name: str
    eval_set_version: str
    prompt_versions: dict[str, str]
    generator_model: str | None
    judge_model: str | None
    llm_provider: str | None
    retrieval_only: bool
    n_items: int
    n_errors: int
    n_unmatched_labels: int
    metrics: dict[str, MetricSummary]
    by_category: dict[str, dict[str, MetricSummary]]
    llm_calls: int
    cache_hits: int
    cache_misses: int
    total_usage: TokenUsage
    estimated_cost_usd: float | None
    bootstrap_seed: int
    bootstrap_resamples: int


def write_results(run_dir: Path, results: list[ItemResult]) -> None:
    with (run_dir / RESULTS_FILE).open("w", encoding="utf-8") as handle:
        for result in results:
            handle.write(result.model_dump_json() + "\n")


def read_results(run_dir: Path) -> list[ItemResult]:
    with (run_dir / RESULTS_FILE).open(encoding="utf-8") as handle:
        return [ItemResult.model_validate_json(line) for line in handle if line.strip()]


def write_summary(run_dir: Path, summary: RunSummary) -> None:
    (run_dir / SUMMARY_FILE).write_text(summary.model_dump_json(indent=2), encoding="utf-8")


def read_summary(run_dir: Path) -> RunSummary:
    return RunSummary.model_validate_json((run_dir / SUMMARY_FILE).read_text(encoding="utf-8"))
