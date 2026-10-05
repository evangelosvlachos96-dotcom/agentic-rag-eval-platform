"""Reproduce the scoped pilot label diagnostic without retrieval or API calls."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from statistics import mean

from ragplatform.evals.results import read_results, read_summary
from ragplatform.evals.sensitivity import ProposedSource, rescore_saved
from ragplatform.ingestion.dataset import read_chunks

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    evidence = ROOT / "docs/evidence/pilot-baselines"
    output = ROOT / "docs/evidence/label-sensitivity"
    output.mkdir(exist_ok=True)
    example = json.loads((evidence / "label-coverage-example.json").read_text())
    proposal = ProposedSource(
        item_id="pilot-003",
        doc_id="96c61294f2cd86dd",
        section_path="Specification",
        evidence=example["text"],
        rationale="This section explicitly defines both required and potentially-missing keys.",
    )
    chunks = {c.id: c for c in read_chunks(ROOT / "data/processed/27b46e65f45d")}
    if chunks[example["retrieved"]["chunk_id"]].content != proposal.evidence:
        raise ValueError("Evidence differs from the pinned indexed corpus")
    eval_hash = hashlib.sha256((ROOT / "eval_sets/v1/items.jsonl").read_bytes()).hexdigest()
    report: dict[str, object] = {
        "status": "Exploratory assistant-proposed label sensitivity; not approved evaluation",
        "scope": "One confirmed label gap; not an exhaustive relevance review",
        "eval_sha256": eval_hash,
        "dataset_version": "27b46e65f45d",
        "llm_calls": 0,
        "proposals": [proposal.model_dump()],
    }
    runs = {}
    pool: dict[tuple[str, str], dict[str, object]] = {}
    lines = [
        "# Label sensitivity diagnostic",
        "",
        "Exploratory assistant-proposed annotation, not an approved evaluation. "
        "One confirmed gap only; the remaining pooled passages are unreviewed. "
        "Original labels and baseline files are unchanged. No API calls or new retrieval.",
        "",
        "| Configuration | Original Hit@8 | Proposed Hit@8 | Original MRR | Proposed MRR |",
        "| --- | --- | --- | --- | --- |",
    ]
    for name in ("bm25_only", "vector_only", "hybrid", "hybrid_rerank"):
        directory = evidence / name
        summary = read_summary(directory)
        if summary.eval_set_version != eval_hash[:12] or summary.dataset_version != "27b46e65f45d":
            raise ValueError("Saved run provenance does not match inputs")
        results = read_results(directory)
        scores = rescore_saved(results, [proposal])
        averages = {
            side: {
                metric: mean(getattr(s, side)[metric] for s in scores)
                for metric in ("hit@1", "hit@8", "mrr")
            }
            for side in ("original", "proposed")
        }
        runs[name] = {
            "run_id": summary.run_id,
            "results_sha256": hashlib.sha256(
                (directory / "results.jsonl").read_bytes()
            ).hexdigest(),
            "averages": averages,
            "items": [s.model_dump() for s in scores],
        }
        old, new = averages["original"], averages["proposed"]
        lines.append(
            f"| {name} | {old['hit@8']:.0%} | {new['hit@8']:.0%} | "
            f"{old['mrr']:.3f} | {new['mrr']:.3f} |"
        )
        for result in results:
            if result.retrieval is None:
                raise ValueError("Missing retrieval")
            for retrieved in result.retrieval.retrieved:
                chunk = chunks[retrieved.chunk_id]
                key = (result.item_id, retrieved.chunk_id)
                pool[key] = {
                    "item_id": result.item_id,
                    "question": result.question,
                    "reference_answer": result.reference_answer,
                    "chunk_id": chunk.id,
                    "doc_id": retrieved.doc_id,
                    "section_path": retrieved.section_path,
                    "text": chunk.content,
                    "review_status": "unreviewed",
                }
    report["runs"] = runs
    report["pooled_passages"] = len(pool)
    (output / "diagnostic.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    # Stable blind ordering: no system names, scores or ranks in the review packet.
    ordered = sorted(pool, key=lambda key: hashlib.sha256("|".join(key).encode()).hexdigest())
    (output / "review-pool.jsonl").write_text(
        "".join(json.dumps(pool[key]) + "\n" for key in ordered), encoding="utf-8"
    )
    lines.extend(
        [
            "",
            f"The review packet contains {len(pool)} unique question/passage pairs "
            "pooled from the four saved top-eight rankings. It hides system names and ranks. "
            "Pooling can still miss relevant passages outside those rankings.",
            "",
            "Only pilot-003 / PEP 655 / Specification is added in this diagnostic, with exact "
            "section matching. Evidence and per-item changes are in diagnostic.json. "
            "An annotation change is not an improvement in the retrieval system.",
            "",
            "Recall, nDCG and complete-source coverage are not recomputed: additional "
            "alternatives do not define exhaustive relevance or independent required facts.",
            "",
            "Next: review pooled evidence and keep proposed annotations separate until accepted. "
            "Next, test the M6 agent with a fake provider before paid evaluation.",
        ]
    )
    (ROOT / "docs/label-sensitivity.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
