"""Tests for comparing two runs with paired bootstrap."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from ragplatform.evals.compare import compare_runs, render_comparison
from ragplatform.evals.results import (
    ItemResult,
    MetricSummary,
    RunSummary,
    write_results,
    write_summary,
)
from ragplatform.models import TokenUsage

if TYPE_CHECKING:
    from pathlib import Path


def _write_run(run_dir: Path, run_id: str, values: dict[str, dict[str, float]]) -> None:
    run_dir.mkdir(parents=True)
    results = [
        ItemResult(
            item_id=item_id,
            question="q",
            category="lookup",
            difficulty="easy",
            answerable=True,
            reference_answer="r",
            metrics=metrics,
        )
        for item_id, metrics in values.items()
    ]
    names = {name for metrics in values.values() for name in metrics}
    summary = RunSummary(
        run_id=run_id,
        config_name="c",
        created_at="2026-01-01T00:00:00+00:00",
        git_commit=None,
        git_dirty=None,
        dataset_version="d",
        eval_set_name="fixture",
        eval_set_version="v",
        prompt_versions={},
        generator_model=None,
        judge_model=None,
        llm_provider=None,
        retrieval_only=True,
        n_items=len(results),
        n_errors=0,
        n_unmatched_labels=0,
        metrics={n: MetricSummary(mean=0.0, ci_lower=0.0, ci_upper=0.0, n=1) for n in names},
        by_category={},
        llm_calls=0,
        cache_hits=0,
        cache_misses=0,
        total_usage=TokenUsage(input_tokens=0, output_tokens=0),
        estimated_cost_usd=None,
        bootstrap_seed=0,
        bootstrap_resamples=10,
    )
    write_results(run_dir, results)
    write_summary(run_dir, summary)


def test_compare_runs_pairs_items_and_reports_distinguishability(tmp_path: Path) -> None:
    a = {f"i{k}": {"mrr": 0.5, "hit@8": float(k % 2)} for k in range(8)}
    b = {f"i{k}": {"mrr": 0.7, "hit@8": float(k % 2), "extra": 1.0} for k in range(8)}
    b["i99"] = {"mrr": 0.0, "hit@8": 0.0, "extra": 1.0}  # not in run A: ignored
    _write_run(tmp_path / "a", "run_a", a)
    _write_run(tmp_path / "b", "run_b", b)

    comparison = compare_runs(tmp_path / "a", tmp_path / "b", seed=0, n_resamples=200)
    assert comparison.n_common_items == 8
    assert comparison.metrics["mrr"].delta == pytest.approx(0.2)
    assert comparison.metrics["mrr"].distinguishable is True
    assert comparison.metrics["hit@8"].delta == 0.0
    assert comparison.metrics["hit@8"].distinguishable is False
    assert comparison.skipped_metrics == ["extra"]

    text = render_comparison(comparison)
    assert "distinguishable from noise" in text
    assert "not distinguishable from noise" in text
    assert "skipped (not in both runs): extra" in text


def test_compare_runs_without_common_items_fails(tmp_path: Path) -> None:
    _write_run(tmp_path / "a", "a", {"x": {"mrr": 1.0}})
    _write_run(tmp_path / "b", "b", {"y": {"mrr": 1.0}})
    with pytest.raises(ValueError, match="no eval items"):
        compare_runs(tmp_path / "a", tmp_path / "b")
