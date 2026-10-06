"""Validate published retrieval evidence and annotation provenance without model calls."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

from ragplatform.evals.bootstrap import bootstrap_ci
from ragplatform.evals.eval_set import load_eval_set
from ragplatform.evals.metrics import hit_at_k, mrr, ndcg_at_k, precision_at_k, recall_at_k
from ragplatform.evals.relevance import section_matches
from ragplatform.evals.results import read_results, read_summary
from ragplatform.pipelines.run_config import RunConfig

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    items, version = load_eval_set(ROOT / "eval_sets", "v1")
    expected = {item.id for item in items}
    approved = {item.id: item for item in items}
    directories = sorted((ROOT / "docs/evidence/pilot-baselines").glob("*/summary.json"))
    directories += sorted((ROOT / "docs/evidence/chunking-ablation").glob("*/summary.json"))
    checked = []
    for path in directories:
        run_dir = path.parent
        summary = read_summary(run_dir)
        results = read_results(run_dir)
        config = RunConfig.model_validate_json(
            (run_dir / "config.json").read_text(encoding="utf-8")
        )
        k = config.retrieval.final_k
        if not summary.retrieval_only or summary.llm_calls or summary.eval_set_version != version:
            raise ValueError(f"Unexpected run provenance: {summary.run_id}")
        if len(results) != len(expected) or {r.item_id for r in results} != expected:
            raise ValueError(f"Wrong question coverage: {summary.run_id}")
        for result in results:
            item = approved[result.item_id]
            if (result.question, result.reference_answer, result.answerable, result.category) != (
                item.question,
                item.reference_answer,
                item.answerable,
                item.category,
            ):
                raise ValueError(f"Evaluation item changed: {result.item_id}")
            if result.retrieval is None or result.error:
                raise ValueError(f"Incomplete retrieval: {result.item_id}")
            for passage in result.retrieval.retrieved:
                labeled = any(
                    passage.doc_id == source.doc_id
                    and section_matches(passage.section_path, source.section_path)
                    for source in item.relevant_sources
                )
                if passage.relevant != labeled:
                    raise ValueError(f"Source flag mismatch: {result.item_id}")
            if not result.answerable:
                if result.metrics:
                    raise ValueError("Unanswerable item included in retrieval metrics")
                continue
            flags = [r.relevant for r in result.retrieval.retrieved]
            relevant = result.retrieval.n_relevant_in_corpus
            calculated = {
                "hit@1": hit_at_k(flags, 1),
                f"hit@{k}": hit_at_k(flags, k),
                "mrr": mrr(flags),
                f"precision@{k}": precision_at_k(flags, k),
                f"recall@{k}": recall_at_k(flags, relevant, k),
                f"ndcg@{k}": ndcg_at_k(flags, relevant, k),
            }
            for name, value in calculated.items():
                if not math.isclose(result.metrics[name], value, abs_tol=1e-12):
                    raise ValueError(f"Item metric mismatch: {result.item_id}/{name}")
        for name, saved in summary.metrics.items():
            sample = [r.metrics[name] for r in results if name in r.metrics]
            actual = bootstrap_ci(sample, summary.bootstrap_resamples, summary.bootstrap_seed)
            for left, right in (
                (saved.mean, actual.mean),
                (saved.ci_lower, actual.lower),
                (saved.ci_upper, actual.upper),
                (saved.n, actual.n),
            ):
                if not math.isclose(left, right, abs_tol=1e-12):
                    raise ValueError(f"Summary mismatch: {summary.run_id}/{name}")
        checked.append(summary.run_id)
    batch = json.loads(
        (ROOT / "docs/evidence/data-quality/blank-annotations.json").read_text(encoding="utf-8")
    )
    results_file = ROOT / "docs/evidence/pilot-baselines/hybrid/results.jsonl"
    if batch["results_sha256"] != hashlib.sha256(results_file.read_bytes()).hexdigest():
        raise ValueError("Annotation batch hash mismatch")
    if any(row["verdict"] is not None for row in batch["rows"]):
        raise ValueError("Blank batch unexpectedly includes judgments")
    report = {
        "status": "passed",
        "eval_version": version,
        "questions_per_run": len(items),
        "verified_runs": checked,
        "checks": [
            "item coverage",
            "retrieval-only provenance",
            "approved question text and source relevance flags",
            "per-item metrics",
            "bootstrap means and intervals",
            "annotation hash and blank labels",
        ],
        "llm_calls": 0,
    }
    output = ROOT / "docs/evidence/readiness"
    output.mkdir(parents=True, exist_ok=True)
    (output / "artifact-checks.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    print(f"Verified {len(checked)} published retrieval runs; no LLM calls")


if __name__ == "__main__":
    main()
