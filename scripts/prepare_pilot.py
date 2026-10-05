"""Build unreviewed pilot candidates from pinned source text; no LLM or network calls.

Run after ingestion: python scripts/prepare_pilot.py --dataset-version VERSION
The authored spec is a review starting point, never a human-validated benchmark.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from pydantic import BaseModel, ConfigDict

from ragplatform.evals.candidates import Candidate, CandidateSource, write_candidates
from ragplatform.evals.models import Category
from ragplatform.ingestion.chunking import ChunkMetadata
from ragplatform.ingestion.corpus import PEPS_COMMIT
from ragplatform.ingestion.dataset import read_chunks, utc_now_iso
from ragplatform.ingestion.loaders import load_file


class Draft(BaseModel):
    model_config = ConfigDict(extra="forbid")

    category: Category
    question: str
    answer: str
    sources: list[tuple[int, str]]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset-version", required=True)
    parser.add_argument("--revision", type=int, default=2)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    chunks = read_chunks(root / "data" / "processed" / args.dataset_version)
    specs = json.loads((root / "eval_sets" / "pilot_spec.json").read_text(encoding="utf-8"))
    candidates: list[Candidate] = []
    lines = [
        "# PEP evaluation pilot: human review required",
        "",
        "24 assistant-authored drafts; four per category. Zero Anthropic API calls.",
        "These are NOT reviewed labels and must not be used for benchmark claims.",
        f"Corpus: python/peps@{PEPS_COMMIT}; dataset: {args.dataset_version}.",
        "",
        "Review answer accuracy, all supporting sources, question category and ambiguity.",
        "Unanswerable examples are easy out-of-domain cases; add harder near-misses later.",
        "Multi-hop drafts follow a PEP reference to a fact in the referenced document.",
        "Verify both steps; multiple labels alone do not prove difficulty.",
        "Use only this pinned corpus. Accept equivalent wording, not only exact answer strings.",
        "For each item, accept, edit or reject via `rag eval review`.",
        "",
    ]
    for index, raw in enumerate(specs, 1):
        spec = Draft.model_validate(raw)
        sources: list[CandidateSource] = []
        links: list[str] = []
        for pep, section in spec.sources:
            doc = load_file(root / "data" / "raw" / "peps" / f"pep-{pep:04d}.rst")
            found = [
                c
                for c in chunks
                if c.document_id == doc.document.id
                and ChunkMetadata.from_chunk(c).section_path == section
            ]
            if not found:
                raise ValueError(f"Missing source PEP {pep}: {section}")
            links.append(
                f"[PEP {pep}: {section}](https://github.com/python/peps/blob/"
                f"{PEPS_COMMIT}/peps/pep-{pep:04d}.rst)"
            )
            for chunk in found:
                sources.append(
                    CandidateSource(
                        chunk_id=chunk.id,
                        doc_id=chunk.document_id,
                        doc_title=doc.title,
                        section_path=section,
                        text=chunk.content,
                    )
                )
        candidate = Candidate(
            id=f"pilot-{index:03d}",
            question=spec.question,
            reference_answer=spec.answer,
            category=spec.category,
            difficulty="medium",
            answerable=spec.category != "unanswerable",
            target_category=spec.category,
            source=sources[0],
            additional_sources=sources[1:],
            model="assistant-authored-draft",
            prompt_version=f"pilot_spec_v{args.revision}",
            created_at=utc_now_iso(),
        )
        candidates.append(candidate)
        lines.extend(
            [
                f"## {candidate.id} / {spec.category}",
                "",
                spec.question,
                "",
                f"**Draft answer:** {spec.answer}",
                "",
                " | ".join(links),
                "",
            ]
        )
        if not candidate.answerable:
            lines.extend(["Attached passage is background only, not supporting evidence.", ""])
        for source in sources:
            lines.extend(
                [
                    f"### {source.doc_title} > {source.section_path}",
                    "",
                    "```text",
                    source.text,
                    "```",
                    "",
                ]
            )
    destination = root / "eval_sets" / "candidates" / f"pilot_v{args.revision}.jsonl"
    if destination.exists():
        raise FileExistsError(
            "Pilot already exists; preserve its review state before regenerating."
        )
    write_candidates(destination, candidates)
    packet = root / "docs" / "pilot-review.md"
    packet.write_text("\n".join(lines), encoding="utf-8")
    concise = [
        f"# Pilot v{args.revision}: final human review",
        "",
        "All 24 entries are UNREVIEWED drafts. No Anthropic API calls were made.",
        "",
        "Use only the pinned PEP corpus. Equivalent correct wording is acceptable.",
        "Accept, edit or reject each entry. Evidence: [full source packet](pilot-review.md).",
        "Unanswerable items test abstention; their attached passages are background only.",
        "",
    ]
    for candidate in candidates:
        concise.extend(
            [
                f"## {candidate.id} / {candidate.category}",
                "",
                candidate.question,
                "",
                f"**Expected answer:** {candidate.reference_answer}",
                "",
            ]
        )
    (root / "docs" / "pilot-questions.md").write_text("\n".join(concise), encoding="utf-8")
    print(f"Prepared {len(candidates)} UNREVIEWED candidates: {destination}")
    print(f"Review packet: {packet}")
    print("Anthropic calls: 0. No eval_sets/v1 labels were created.")


if __name__ == "__main__":
    main()
