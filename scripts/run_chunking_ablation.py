"""Run three cost-free pilot ablations and compare against the frozen BM25 baseline."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import structlog

from ragplatform.evals.compare import compare_runs
from ragplatform.evals.eval_set import load_eval_set
from ragplatform.evals.results import read_summary
from ragplatform.evals.runner import make_run_id
from ragplatform.ingestion.chunking import ChunkingConfig
from ragplatform.pipelines.sweep import ChunkingVariant, run_variant

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    structlog.configure(wrapper_class=structlog.make_filtering_bound_logger(20))
    items, version = load_eval_set(ROOT / "eval_sets", "v1")
    baseline = ROOT / "docs/evidence/pilot-baselines/bm25_only"
    original = read_summary(baseline)
    if original.eval_set_version != version:
        raise ValueError("Baseline label version differs")
    evidence = ROOT / "docs/evidence/chunking-ablation"
    if evidence.exists():
        raise FileExistsError("Existing experiment evidence is immutable; use a new destination")
    variants = [
        ChunkingVariant(name="bm25_tokens250", chunking=ChunkingConfig(max_tokens=250)),
        ChunkingVariant(name="bm25_tokens600", chunking=ChunkingConfig(max_tokens=600)),
        ChunkingVariant(name="bm25_noheader", chunking=ChunkingConfig(contextual_header=False)),
    ]
    summaries = {"bm25_tokens400": original.model_dump()}
    comparisons = {}
    evidence.mkdir(parents=True)
    for variant in variants:
        directory = ROOT / "experiments/runs" / make_run_id(variant.name)
        summary = run_variant(
            variant,
            raw_dir=ROOT / "data/raw/peps",
            processed_root=ROOT / "data/ablations",
            run_dir=directory,
            items=items,
            eval_version=version,
            repo_dir=ROOT,
        )
        comparisons[variant.name] = compare_runs(baseline, directory).model_dump()
        summaries[variant.name] = summary.model_dump()
        shutil.copytree(directory, evidence / variant.name)
    payload = {
        "eval_version": version,
        "llm_calls": 0,
        "baseline": original.run_id,
        "summaries": summaries,
        "paired_comparisons": comparisons,
    }
    (evidence / "comparison.json").write_text(
        json.dumps(payload, indent=2) + "\n", encoding="utf-8"
    )
    lines = [
        "# Chunking and contextual-header ablation",
        "",
        "Real local BM25 retrieval, no model API calls. The same 24 owner-approved questions "
        "are used throughout; 20 answerable items contribute metrics. Original labels are "
        "unchanged. This is an exploratory pilot, not a held-out benchmark.",
        "",
        "| Variant | Hit@1 | Hit@8 | MRR | MRR change vs 400 | Paired 95% CI |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for name, raw in summaries.items():
        metrics = raw["metrics"]
        delta, interval = "baseline", "-"
        if name in comparisons:
            metric = comparisons[name]["metrics"]["mrr"]
            delta = f"{metric['delta']:+.3f}"
            interval = f"[{metric['lower']:+.3f}, {metric['upper']:+.3f}]"
        lines.append(
            f"| {name} | {metrics['hit@1']['mean']:.0%} | "
            f"{metrics['hit@8']['mean']:.0%} | {metrics['mrr']['mean']:.3f} | "
            f"{delta} | {interval} |"
        )
    lines.extend(
        [
            "",
            "The default uses a 400 approximate-token budget, 15% overlap and "
            "title/section headers in index text. The 250/600 variants change only the token "
            "budget; noheader changes only the indexing header. Structure boundaries can "
            "produce smaller chunks. Dedup settings, BM25 parameters and top-eight cutoff "
            "are fixed. Dataset manifests preserve source hashes and chunking parameters.",
            "",
            "Paired intervals use 1,000 resamples and seed 0. Questions overlap in topic; "
            "the sample is small, labels are not exhaustive, and no multiplicity correction "
            "is applied. Recall and nDCG denominators change with chunking, so the headline "
            "comparison uses Hit@k and MRR. Answer quality and abstention are not measured.",
            "",
            "Retrieval mode and reranking ablations are documented in [baseline results]"
            "(baseline-results.md). These experiments do not justify changing defaults "
            "without a broader reviewed evaluation set.",
            "",
            "## Saved runs",
            "",
        ]
    )
    lines.extend(f"- `{raw['run_id']}`" for raw in summaries.values())
    (ROOT / "docs/chunking-results.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
