"""Markdown report for a run: provenance, metrics with CIs, category breakdown, worst failures."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence

    from ragplatform.evals.results import ItemResult, MetricSummary, RunSummary

WORST_N = 10


def _metric_table(metrics: dict[str, MetricSummary]) -> list[str]:
    lines = ["| metric | mean | 95% CI | n |", "| --- | ---: | ---: | ---: |"]
    for name, m in sorted(metrics.items()):
        lines.append(f"| {name} | {m.mean:.3f} | [{m.ci_lower:.3f}, {m.ci_upper:.3f}] | {m.n} |")
    return lines


def failure_score(result: ItemResult) -> float:
    """Higher is worse. Errors and wrong abstention decisions dominate."""
    if result.error:
        return 100.0
    score = 0.0
    checks = result.checks
    if checks is not None:
        score += 5.0 * checks.missed_abstention + 4.0 * checks.unnecessary_abstention
        score += 2.0 * checks.answered_without_citations + 1.0 * (not checks.citations_valid)
    metrics = result.metrics
    score += 3.0 * (1.0 - metrics.get("correctness", 1.0))
    score += 2.0 * (1.0 - metrics.get("faithfulness", 1.0))
    score += 1.0 * (1.0 - metrics.get("relevance", 1.0))
    hit_keys = [k for k in metrics if k.startswith("hit@") and k != "hit@1"]
    if hit_keys:
        score += 2.0 * (1.0 - metrics[hit_keys[0]])
    return score


def worst_failures(results: Sequence[ItemResult], n: int = WORST_N) -> list[ItemResult]:
    scored = [(failure_score(r), r) for r in results]
    scored = [(s, r) for s, r in scored if s > 0]
    scored.sort(key=lambda pair: (-pair[0], pair[1].item_id))
    return [r for _, r in scored[:n]]


def _render_failure(result: ItemResult) -> list[str]:
    kind = "answerable" if result.answerable else "unanswerable"
    lines = [
        f"### {result.item_id} ({result.category}, {kind})",
        "",
        f"**Question:** {result.question}",
        "",
        f"**Reference:** {result.reference_answer}",
        "",
    ]
    if result.error:
        lines += [f"**Error:** `{result.error}`", ""]
    if result.retrieval is not None:
        lines.append("**Retrieved sections:**")
        lines.append("")
        for r in result.retrieval.retrieved:
            mark = "✅" if r.relevant else "❌"
            where = f"{r.doc_title} > {r.section_path}" if r.section_path else r.doc_title
            lines.append(f"- {mark} [{r.rank}] {where} (`{r.chunk_id}`)")
        if not result.retrieval.labels_matched:
            lines.append("- ⚠️ labels matched no chunk in this dataset version")
        lines.append("")
    if result.answer is not None:
        state = "ABSTAINED" if result.answer.abstained else "answered"
        cited = ", ".join(c.chunk_id for c in result.answer.citations) or "none"
        lines += [f"**Answer ({state}, citations: {cited}):** {result.answer.text}", ""]
        if result.answer.invalid_citations:
            lines += [f"**Invalid citations removed:** {result.answer.invalid_citations}", ""]
    if result.judges is not None:
        if result.judges.correctness is not None:
            c = result.judges.correctness
            lines += [
                f"**Correctness judge ({'correct' if c.correct else 'incorrect'}):** {c.reasoning}",
                "",
            ]
        if result.judges.faithfulness is not None:
            unsupported = [cl for cl in result.judges.faithfulness.claims if not cl.supported]
            if unsupported:
                lines.append("**Unsupported claims:**")
                lines.append("")
                for claim in unsupported:
                    lines.append(f"- {claim.claim} — {claim.reasoning}")
                lines.append("")
        if result.judges.relevance is not None and not result.judges.relevance.relevant:
            lines += [
                f"**Relevance judge (not relevant):** {result.judges.relevance.reasoning}",
                "",
            ]
    if result.metrics:
        shown = ", ".join(f"{k}={v:.2f}" for k, v in sorted(result.metrics.items()))
        lines += [f"**Metrics:** {shown}", ""]
    return lines


def render_report(summary: RunSummary, results: Sequence[ItemResult]) -> str:
    usage = summary.total_usage
    cost = summary.estimated_cost_usd if summary.estimated_cost_usd is not None else "n/a"
    lines: list[str] = [
        f"# Eval run `{summary.run_id}`",
        "",
        f"- config: `{summary.config_name}`",
        f"- created: {summary.created_at}",
        f"- git: `{summary.git_commit or 'unknown'}`{' (dirty)' if summary.git_dirty else ''}",
        f"- dataset version: `{summary.dataset_version}`",
        f"- eval set: `{summary.eval_set_name}` @ `{summary.eval_set_version}` "
        f"({summary.n_items} items)",
        f"- prompts: {summary.prompt_versions}",
        f"- generator: `{summary.generator_model}`  judge: `{summary.judge_model}`  "
        f"provider: `{summary.llm_provider}`",
        f"- retrieval only: {summary.retrieval_only}",
        f"- LLM calls: {summary.llm_calls} (cache hits {summary.cache_hits}, "
        f"misses {summary.cache_misses}); tokens in/out: "
        f"{usage.input_tokens}/{usage.output_tokens}; estimated cost: {cost}",
        f"- errors: {summary.n_errors}; items whose labels matched no chunk: "
        f"{summary.n_unmatched_labels}",
        f"- bootstrap: {summary.bootstrap_resamples} resamples, seed {summary.bootstrap_seed}",
        "",
    ]
    if summary.llm_provider and "fake" in summary.llm_provider:
        lines += [
            "> **Placeholder run.** The LLM provider was the fake provider; generation and judge "
            "numbers below are canned and mean nothing.",
            "",
        ]
    lines += ["## Metrics", "", *_metric_table(summary.metrics), ""]
    if summary.by_category:
        lines += ["## By category", ""]
        for category, metrics in sorted(summary.by_category.items()):
            lines += [f"### {category}", "", *_metric_table(metrics), ""]
    failures = worst_failures(results)
    lines += [f"## Worst {len(failures)} failures", ""]
    if not failures:
        lines.append("No failures by the report's scoring.")
    for result in failures:
        lines += _render_failure(result)
    return "\n".join(lines).rstrip() + "\n"
