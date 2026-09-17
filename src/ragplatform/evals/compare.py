"""Compare two runs on the same eval items with paired bootstrap CIs."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import BaseModel, ConfigDict, Field

from ragplatform.evals.bootstrap import PairedComparison, paired_bootstrap
from ragplatform.evals.results import read_results, read_summary

if TYPE_CHECKING:
    from pathlib import Path


class RunComparison(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    run_a: str
    run_b: str
    eval_set_version_a: str
    eval_set_version_b: str
    n_common_items: int = Field(ge=0)
    metrics: dict[str, PairedComparison]
    skipped_metrics: list[str] = Field(
        default_factory=list, description="Metrics missing from one run or with no common items."
    )


def compare_runs(
    run_a_dir: Path, run_b_dir: Path, seed: int = 0, n_resamples: int = 1000
) -> RunComparison:
    summary_a = read_summary(run_a_dir)
    summary_b = read_summary(run_b_dir)
    results_a = {r.item_id: r for r in read_results(run_a_dir)}
    results_b = {r.item_id: r for r in read_results(run_b_dir)}
    common = sorted(set(results_a) & set(results_b))
    if not common:
        raise ValueError("the two runs share no eval items")

    names = sorted(set(summary_a.metrics) | set(summary_b.metrics))
    metrics: dict[str, PairedComparison] = {}
    skipped: list[str] = []
    for name in names:
        pairs = [
            (results_a[i].metrics[name], results_b[i].metrics[name])
            for i in common
            if name in results_a[i].metrics and name in results_b[i].metrics
        ]
        if not pairs:
            skipped.append(name)
            continue
        a_values = [p[0] for p in pairs]
        b_values = [p[1] for p in pairs]
        metrics[name] = paired_bootstrap(a_values, b_values, n_resamples=n_resamples, seed=seed)
    return RunComparison(
        run_a=summary_a.run_id,
        run_b=summary_b.run_id,
        eval_set_version_a=summary_a.eval_set_version,
        eval_set_version_b=summary_b.eval_set_version,
        n_common_items=len(common),
        metrics=metrics,
        skipped_metrics=skipped,
    )


def render_comparison(comparison: RunComparison) -> str:
    lines = [
        f"A = {comparison.run_a}",
        f"B = {comparison.run_b}",
        f"common items: {comparison.n_common_items}",
    ]
    if comparison.eval_set_version_a != comparison.eval_set_version_b:
        lines.append(
            "WARNING: the runs used different eval set versions "
            f"({comparison.eval_set_version_a} vs {comparison.eval_set_version_b})"
        )
    lines += [
        "",
        f"{'metric':<22} {'A':>7} {'B':>7} {'delta (B-A)':>12} {'95% CI':>18}  verdict",
    ]
    for name, m in sorted(comparison.metrics.items()):
        verdict = (
            "distinguishable from noise" if m.distinguishable else "not distinguishable from noise"
        )
        lines.append(
            f"{name:<22} {m.mean_a:>7.3f} {m.mean_b:>7.3f} {m.delta:>+12.3f} "
            f"[{m.lower:>+7.3f}, {m.upper:>+7.3f}]  {verdict}"
        )
    if comparison.skipped_metrics:
        lines.append("")
        lines.append(f"skipped (not in both runs): {', '.join(comparison.skipped_metrics)}")
    return "\n".join(lines)
