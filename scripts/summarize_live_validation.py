"""Verify and summarize real paid artifacts; never calls a model or invents reviews."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

from ragplatform.data_quality.annotations import export_batch
from ragplatform.evals.bootstrap import bootstrap_ci
from ragplatform.evals.compare import compare_runs
from ragplatform.evals.eval_set import load_eval_set
from ragplatform.evals.results import read_results, read_summary
from ragplatform.ingestion.dataset import read_chunks
from ragplatform.llm.budget import BudgetLedger
from ragplatform.llm.pricing import load_pricing

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "docs/evidence/live-validation"
ORDER = ("bm25_only", "vector_only", "hybrid", "hybrid_rerank")


def main() -> None:
    items, version = load_eval_set(ROOT / "eval_sets", "v1")
    approved = {item.id: item for item in items}
    ledger = BudgetLedger.model_validate_json(
        (EVIDENCE / "budget.json").read_text(encoding="utf-8")
    )
    pricing = load_pricing(ROOT / "configs/pricing.yaml")
    if any(r.status not in {"completed", "reserved_after_review"} for r in ledger.records):
        raise ValueError("Incomplete accounting; investigate before reporting final cost")
    for record in ledger.records:
        if record.status == "reserved_after_review" and record.recovery_note:
            continue
        if record.usage is None or record.actual_usd is None:
            raise ValueError("Missing usage")
        if not math.isclose(
            record.actual_usd, pricing.cost_usd(record.model, record.usage), abs_tol=1e-12
        ):
            raise ValueError("Ledger pricing mismatch")
    if ledger.committed_usd > ledger.limit_usd:
        raise ValueError("Budget exceeded")
    known_cost = sum(r.actual_usd or 0 for r in ledger.records)
    unknown_reserve = sum(r.reserved_usd for r in ledger.records if r.actual_usd is None)
    unknown_calls = sum(r.actual_usd is None for r in ledger.records)
    rows = []
    hashes = {}
    examples = []
    summaries = {}
    for name in ORDER:
        directory = EVIDENCE / name
        summary = read_summary(directory)
        results = read_results(directory)
        if summary.retrieval_only or "anthropic" not in (summary.llm_provider or ""):
            raise ValueError("Not real Anthropic generation evidence")
        if summary.n_errors or summary.eval_set_version != version:
            raise ValueError("Incomplete run or evaluation mismatch")
        if len(results) != len(items) or {r.item_id for r in results} != set(approved):
            raise ValueError("Incorrect coverage")
        for result in results:
            item = approved[result.item_id]
            if result.question != item.question or result.reference_answer != item.reference_answer:
                raise ValueError("Approved item changed")
            if result.error or result.answer is None or result.checks is None:
                raise ValueError("Incomplete generated answer")
        for key, metric in summary.metrics.items():
            values = [r.metrics[key] for r in results if key in r.metrics]
            ci = bootstrap_ci(values, summary.bootstrap_resamples, summary.bootstrap_seed)
            if metric.n != ci.n or any(
                not math.isclose(a, b, abs_tol=1e-12)
                for a, b in (
                    (metric.mean, ci.mean),
                    (metric.ci_lower, ci.lower),
                    (metric.ci_upper, ci.upper),
                )
            ):
                raise ValueError(f"Summary mismatch: {name}/{key}")
        correct = summary.metrics["correctness"]
        faith = summary.metrics.get("faithfulness")
        abstain = summary.metrics["correct_abstention"]
        rows.append(
            f"| {name} | {correct.mean:.0%} ({correct.n}) | "
            f"[{correct.ci_lower:.0%}, {correct.ci_upper:.0%}] | "
            f"{faith.mean:.1%} ({faith.n}) | {abstain.mean:.0%} ({abstain.n}) |"
            if faith
            else f"| {name} | {correct.mean:.0%} | — | — | {abstain.mean:.0%} |"
        )
        summaries[name] = summary.model_dump(mode="json")
        hashes[name] = hashlib.sha256((directory / "results.jsonl").read_bytes()).hexdigest()
        if name == "hybrid":
            selected = []
            for criterion in ("correct", "incorrect", "grounding concern", "unanswerable"):
                match = next(
                    (
                        r
                        for r in results
                        if (
                            (criterion == "correct" and r.metrics.get("correctness") == 1)
                            or (criterion == "incorrect" and r.metrics.get("correctness") == 0)
                            or (
                                criterion == "grounding concern"
                                and r.metrics.get("faithfulness", 1) < 1
                            )
                            or (criterion == "unanswerable" and not r.answerable)
                        )
                    ),
                    None,
                )
                if match is not None:
                    selected.append((criterion, match))
            for kind, result in selected:
                examples.append({"selection": kind, "result": result.model_dump(mode="json")})
    comparisons = {
        name: compare_runs(EVIDENCE / "bm25_only", EVIDENCE / name).model_dump(mode="json")
        for name in ORDER[1:]
    }
    corpus = read_chunks(ROOT / "data/processed/27b46e65f45d")
    batch = export_batch(EVIDENCE / "hybrid", corpus)
    (EVIDENCE / "human-review-blank.json").write_text(
        batch.model_dump_json(indent=2) + "\n", encoding="utf-8"
    )
    agents = [
        json.loads(path.read_text(encoding="utf-8"))
        for path in sorted((EVIDENCE / "agents").glob("*.json"))
    ]
    if any(agent["placeholder"] for agent in agents):
        raise ValueError("Placeholder agent")
    report = {
        "status": "verified",
        "completion_attempts": len(ledger.records),
        "known_usage_cost_usd": known_cost,
        "unmetered_reserved_usd": unknown_reserve,
        "committed_usd": ledger.committed_usd,
        "unknown_usage_calls": unknown_calls,
        "input_tokens": sum(r.usage.input_tokens for r in ledger.records if r.usage),
        "output_tokens": sum(r.usage.output_tokens for r in ledger.records if r.usage),
        "results_sha256": hashes,
        "summaries": summaries,
        "comparisons": comparisons,
        "examples": examples,
        "human_review": "pending; blank batch only",
        "agent_demonstrations": len(agents),
    }
    (EVIDENCE / "analysis.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# Live validation results",
        "",
        "Real API evaluation on the frozen 24-question owner-approved PEP pilot. "
        "These are automated-judge measurements, not human-certified accuracy.",
        "",
        "Generator: Claude Sonnet 5. Judges: Claude Haiku 4.5. "
        "Same prompts, dataset and generation settings across four retrieval configurations.",
        "",
        "| Configuration | Correctness (n) | 95% bootstrap CI | Faithfulness (n) | "
        "Correct abstention (n) |",
        "| --- | --- | --- | --- | --- |",
        *rows,
        "",
        "Correctness includes zero for unnecessary abstention on answerable questions. "
        "Faithfulness is the mean supported-claim fraction among answers judged; "
        "abstentions are excluded. Correct abstention uses the four unanswerable questions.",
        "An all-success bootstrap interval does not establish perfect population accuracy. "
        "Labeled-source retrieval hits and automated answer judgments measure different "
        "properties; neither substitutes for independent human review.",
        "",
        "## Cost and execution",
        "",
        f"{len(ledger.records)} API completion attempts; "
        f"{report['input_tokens']:,} input and {report['output_tokens']:,} output tokens. "
        f"Estimated reported token cost **USD {known_cost:.4f}**, plus "
        f"**USD {unknown_reserve:.4f} retained for unmetered failures (n={unknown_calls})**, "
        "including the preliminary pilot and agent demonstrations. "
        "All dispatch reservations stayed within the shared USD 3 ceiling. "
        "Token totals exclude unmetered failures. Actual billing remains the account "
        "invoice's authority.",
        "",
        "The pilot's identical requests can be cache hits in the full BM25 run. "
        "The session ledger counts each paid request once; cached outputs are not "
        "independent repeated trials. No repeated attempts were made to select favorable results.",
        "",
        "An initial provider failure interrupted BM25 evaluation. The stopped run is retained "
        "under `interrupted-attempts`; recovery kept the entire failed-call allowance, "
        "reused completed responses, and paced subsequent requests. The original failure "
        "cause was not recorded beyond LLMError; it is not assumed to be free.",
        "",
        "## Paired correctness comparisons against BM25",
        "",
    ]
    for name, comparison in comparisons.items():
        metric = comparison["metrics"]["correctness"]
        lines.append(
            f"- {name}: delta {metric['delta']:+.1%}; "
            f"95% CI [{metric['lower']:+.1%}, {metric['upper']:+.1%}]."
        )
    lines += [
        "",
        "1,000 paired bootstrap resamples, seed 0. Exploratory comparisons without "
        "multiplicity correction; related questions and incomplete labels limit generalization.",
        "",
        "## Agent demonstrations",
        "",
    ]
    for agent in agents:
        lines.append(
            f"- {agent['question']} — {agent['stop_reason']}; {len(agent['steps'])} step(s)."
        )
    lines += [
        "",
        "Single bounded attempts with real BM25 search. Structural citation checks "
        "do not establish factual correctness, and four trajectories are not a pass@k study.",
        "",
        "## Review and provenance",
        "",
        "Full answers, judge reasoning, citations and run reports are in "
        "[the evidence archive](evidence/live-validation/). `analysis.json` records "
        "verified result hashes, recalculated bootstrap intervals and paired comparisons. "
        "`human-review-blank.json` is prepared for review; no human verdicts are invented.",
        "",
        "The run summaries retain commit and dirty-working-tree provenance. "
        "`execution-changes.patch` records the budget-recovery and pacing changes "
        "relative to the recorded base commit; evaluation prompts and model settings "
        "were unchanged during recovery.",
        "",
        "Human-judge calibration, broader relevance review and a separate held-out "
        "benchmark remain uncompleted. This is a completed small live validation, "
        "not proof of production readiness.",
        "",
    ]
    (ROOT / "docs/live-results.md").write_text("\n".join(lines), encoding="utf-8")
    print(
        f"Verified four live runs; {len(agents)} agent demonstrations; ${ledger.committed_usd:.4f}"
    )


if __name__ == "__main__":
    main()
