"""Archive real retrieval runs and produce a pilot report. No models or APIs are called."""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import shutil
from importlib.metadata import version as package_version
from pathlib import Path

from ragplatform.evals.compare import compare_runs, render_comparison
from ragplatform.evals.eval_set import load_eval_set
from ragplatform.evals.relevance import section_matches
from ragplatform.evals.results import read_results, read_summary
from ragplatform.ingestion.dataset import read_chunks


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("runs", nargs=4, type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    items, version = load_eval_set(root / "eval_sets", "v1")
    runs = {read_summary(path).config_name: path for path in args.runs}
    order = ["bm25_only", "vector_only", "hybrid", "hybrid_rerank"]
    if set(runs) != set(order):
        raise ValueError("Provide exactly one run for each baseline configuration")
    destination = root / "docs" / "evidence" / "pilot-baselines"
    destination.mkdir(parents=True, exist_ok=True)
    summaries = {name: read_summary(runs[name]) for name in order}
    expected_ids = {item.id for item in items}
    diagnostics: dict[str, list[dict[str, object]]] = {}
    for name in order:
        summary = summaries[name]
        if not summary.retrieval_only or summary.llm_calls or summary.n_errors:
            raise ValueError(f"{name}: expected successful retrieval-only run with zero LLM calls")
        if summary.eval_set_version != version or summary.dataset_version != "27b46e65f45d":
            raise ValueError(f"{name}: dataset/eval version mismatch")
        results = {result.item_id: result for result in read_results(runs[name])}
        if set(results) != expected_ids:
            raise ValueError(f"{name}: item IDs differ")
        output = destination / name
        output.mkdir(exist_ok=True)
        for filename in ("config.json", "results.jsonl", "summary.json", "report.md"):
            shutil.copy2(runs[name] / filename, output / filename)
        diagnostics[name] = []
        for item in items:
            if not item.answerable:
                continue
            result = results[item.id]
            if result.retrieval is None:
                raise ValueError("Missing retrieval results")
            retrieved = result.retrieval.retrieved
            covered = sum(
                any(
                    r.doc_id == source.doc_id
                    and section_matches(r.section_path, source.section_path)
                    for r in retrieved
                )
                for source in item.relevant_sources
            )
            diagnostics[name].append(
                {
                    "id": item.id,
                    "category": item.category,
                    "question": item.question,
                    "hit_at_8": result.metrics["hit@8"],
                    "labeled_sources": len(item.relevant_sources),
                    "covered_sources": covered,
                    "all_labeled_sources": covered == len(item.relevant_sources),
                    "top_result": f"{retrieved[0].doc_title} > {retrieved[0].section_path}"
                    if retrieved
                    else None,
                }
            )
    comparisons = {}
    for a, b in [
        ("bm25_only", "vector_only"),
        ("bm25_only", "hybrid"),
        ("bm25_only", "hybrid_rerank"),
        ("hybrid", "hybrid_rerank"),
    ]:
        comparison = compare_runs(runs[a], runs[b], seed=0)
        comparisons[f"{a}_vs_{b}"] = comparison.model_dump()
        (destination / f"{a}_vs_{b}.txt").write_text(
            render_comparison(comparison), encoding="utf-8"
        )
    data = {
        "scope": "Owner-approved pilot; retrieval only, not generation quality",
        "eval_version": version,
        "dataset_version": "27b46e65f45d",
        "n_items": len(items),
        "n_answerable": sum(i.answerable for i in items),
        "summaries": {name: s.model_dump() for name, s in summaries.items()},
        "comparisons": comparisons,
        "source_coverage": diagnostics,
        "anthropic_api_calls": 0,
    }
    (destination / "comparison.json").write_text(json.dumps(data, indent=2), encoding="utf-8")
    chunks = {c.id: c for c in read_chunks(root / "data/processed/27b46e65f45d")}
    example = next(r for r in read_results(runs["bm25_only"]) if r.item_id == "pilot-003")
    if example.retrieval is None:
        raise ValueError("Missing case-study retrieval")
    specification = next(
        r
        for r in example.retrieval.retrieved
        if r.doc_id == "96c61294f2cd86dd" and r.section_path == "Specification"
    )
    case = {
        "item": next(i.model_dump() for i in items if i.id == "pilot-003"),
        "retrieved": specification.model_dump(),
        "text": chunks[specification.chunk_id].content,
        "finding": "The specification answers the question but is outside the Abstract label.",
        "action": "Preserve scores; propose alternative labels for a separate human review.",
    }
    (destination / "label-coverage-example.json").write_text(
        json.dumps(case, indent=2), encoding="utf-8"
    )
    lines = [
        "# Reviewed PEP pilot: retrieval baselines",
        "",
        "24 owner-approved questions; retrieval metrics use the 20 answerable items.",
        "Four unanswerable items are excluded from these scores. Generation and abstention",
        "were not evaluated. All four runs made **zero Anthropic calls**.",
        "",
        f"Dataset `27b46e65f45d`; evaluation set `v1@{version}`.",
        "",
        "## Measured results",
        "",
        "Hit@8 means at least one labeled passage appears in the top eight results.",
        "It is not answer accuracy. MRR measures the rank of the first labeled passage.",
        "The 24 common item IDs include four unanswerable items; each metric uses n=20.",
        "",
        "| Configuration | Hit@1 | Hit@8 (95% CI) | MRR (95% CI) | nDCG@8 | Recall@8 |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for name, summary in summaries.items():
        metrics = summary.metrics
        hit, mrr = metrics["hit@8"], metrics["mrr"]
        lines.append(
            f"| {name} | {metrics['hit@1'].mean:.3f} | {hit.mean:.3f} "
            f"[{hit.ci_lower:.3f}, {hit.ci_upper:.3f}] | {mrr.mean:.3f} "
            f"[{mrr.ci_lower:.3f}, {mrr.ci_upper:.3f}] | "
            f"{metrics['ndcg@8'].mean:.3f} | {metrics['recall@8'].mean:.3f} |"
        )
    lines += [
        "",
        "## Paired comparisons",
        "",
        "95% percentile bootstrap, 1,000 resamples, seed 0.",
        "Exploratory intervals on this pilot; no multiple-comparison correction.",
        "",
    ]
    for name in comparisons:
        lines += ["```text", (destination / f"{name}.txt").read_text(encoding="utf-8"), "```", ""]
    lines += [
        "## Multi-source diagnostic",
        "",
        "Counts questions whose top eight results cover every labeled source location.",
        "This tests evidence coverage, not whether the answer is correct.",
        "",
        "| Configuration | Multi-hop: all sources | Comparison: all sources |",
        "|---|---:|---:|",
    ]
    for name in order:
        counts = [
            sum(
                bool(r["all_labeled_sources"])
                for r in diagnostics[name]
                if r["category"] == category
            )
            for category in ("multi_hop", "comparison")
        ]
        lines.append(f"| {name} | {counts[0]}/4 | {counts[1]}/4 |")
    lines += [
        "",
        "## Findings and recommended next step",
        "",
        "Hybrid has the highest observed hit@8 (16/20) and MRR, but its hit@8/MRR improvements",
        "over BM25 do not exclude zero in the paired 95% intervals. Some other exploratory",
        "metrics favor hybrid; these are not corrected for multiple comparisons.",
        "",
        "Reranking lowers observed hit@8 from 16/20 to 14/20. Its paired MRR change is",
        "-0.061, with interval [-0.198, 0.068]; this is not evidence of a reliable regression.",
        "",
        "**Confirmed label blind spot:** for `pilot-003`, BM25 retrieves PEP 655's Specification",
        "at rank 2, which explicitly defines Required and NotRequired. The accepted label names",
        "only its Abstract, so the scorer records a miss. The full passage and metadata are in",
        "[the evidence record](evidence/pilot-baselines/label-coverage-example.json).",
        "",
        "Before choosing a configuration or starting the agent phase, review pooled retrieved",
        "passages from all four systems for additional relevant sources. Review them without",
        "system/rank identifiers where practical, version the revised labels separately, and",
        "rescore these saved rankings without model/API calls. Then expand the small pilot.",
        "",
        "No labels or retrieval defaults were changed in response to these scores.",
        "",
        "",
        "## Reproduction and limits",
        "",
        "Runs used BAAI/bge-small-en-v1.5 and cross-encoder/ms-marco-MiniLM-L-6-v2",
        "from the local cache, with Hugging Face/Transformers offline mode enabled.",
        "Candidate pool 50, final k=8, RRF k=60; existing configs were not tuned to results.",
        "The embedding query prefix was empty, matching the existing default.",
        "Model revisions and file hashes are recorded in provenance.json.",
        "",
        "This small pilot has overlapping topics, source labels that are not exhaustive,",
        "and easy out-of-domain negatives. A miss can retrieve useful but unlabeled text.",
        "Chunk recall penalizes retrieving only part of a labeled multi-chunk section.",
        "Bootstrap intervals assume independent items; topical overlap weakens that assumption.",
        "Do not interpret these scores as production readiness or broad statistical proof.",
        "Labels were frozen before baseline execution; no labels were changed to improve scores.",
        "",
        "## Run IDs",
        "",
    ]
    for name, summary in summaries.items():
        lines.append(
            f"- `{summary.run_id}` — [raw report](evidence/pilot-baselines/{name}/report.md)"
        )
    lines += [
        "",
        "## Showcase screenshots",
        "",
        "![Pilot retrieval results](images/pilot-baseline-results.png)",
        "",
        "![Pilot findings](images/pilot-baseline-findings.png)",
        "",
        "Screenshots of the local report; not a deployed application.",
    ]
    (root / "docs" / "baseline-results.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    provenance = {
        "python": platform.python_version(),
        "platform": platform.system(),
        "dependencies": {
            name: package_version(name)
            for name in ("numpy", "torch", "sentence-transformers", "transformers", "rank-bm25")
        },
        "uv_lock_sha256": hashlib.sha256((root / "uv.lock").read_bytes()).hexdigest(),
        "source_hashes": {
            str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted((root / "src").rglob("*.py"))
        },
        "eval_sha256": hashlib.sha256((root / "eval_sets/v1/items.jsonl").read_bytes()).hexdigest(),
        "model_revisions": {},
        "execution": {
            "HF_HUB_OFFLINE": "1",
            "TRANSFORMERS_OFFLINE": "1",
            "OMP_NUM_THREADS": "4",
            "MKL_NUM_THREADS": "4",
        },
    }
    cache = Path.home() / ".cache" / "huggingface" / "hub"
    for model in ("BAAI/bge-small-en-v1.5", "cross-encoder/ms-marco-MiniLM-L-6-v2"):
        ref = cache / ("models--" + model.replace("/", "--")) / "refs" / "main"
        provenance["model_revisions"][model] = ref.read_text().strip()
    (destination / "provenance.json").write_text(json.dumps(provenance, indent=2), encoding="utf-8")
    print("Wrote docs/baseline-results.md and archived all raw evidence.")


if __name__ == "__main__":
    main()
