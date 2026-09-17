"""Synthetic eval candidates: stratified chunk sampling plus LLM-written questions.

Candidates are *not* eval items. They go to ``eval_sets/candidates/<timestamp>.jsonl``
with the source chunk attached, and only become items after a human accepts
them in ``rag eval review``.

Sampling is stratified two ways: chunks are drawn round-robin across documents
(so long PEPs do not dominate), and target categories cycle through the
taxonomy with a fixed share of unanswerable prompts. Both use a seeded RNG.
"""

from __future__ import annotations

import random
from collections import defaultdict
from typing import TYPE_CHECKING, cast

import structlog
from pydantic import BaseModel, ConfigDict, Field

from ragplatform.evals.models import ANSWERABLE_CATEGORIES, Category, Difficulty
from ragplatform.ingestion.chunking import ChunkMetadata
from ragplatform.ingestion.dataset import utc_now_iso
from ragplatform.llm.provider import CompletionRequest
from ragplatform.llm.structured import StructuredOutputError, complete_structured
from ragplatform.prompts import load_prompt

if TYPE_CHECKING:
    from collections.abc import Sequence
    from pathlib import Path

    from ragplatform.evals.taxonomy import Taxonomy
    from ragplatform.llm.provider import LLMProvider
    from ragplatform.models import Chunk

log = structlog.get_logger(__name__)


class CandidateSource(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    chunk_id: str
    doc_id: str
    doc_title: str
    section_path: str
    text: str


class CandidateOutput(BaseModel):
    """The JSON the candidate prompt asks for."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    question: str = Field(min_length=1)
    reference_answer: str = Field(min_length=1)
    category: Category
    difficulty: Difficulty


class Candidate(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    id: str
    question: str
    reference_answer: str
    category: Category
    difficulty: Difficulty
    answerable: bool
    target_category: str = Field(description="Category the prompt asked for.")
    source: CandidateSource
    model: str
    prompt_version: str
    created_at: str


def stratified_sample(chunks: Sequence[Chunk], n: int, seed: int = 0) -> list[Chunk]:
    """Round-robin over documents, random order within each, until ``n`` chunks."""
    rng = random.Random(seed)  # noqa: S311 - sampling, not security
    by_doc: dict[str, list[Chunk]] = defaultdict(list)
    for chunk in chunks:
        by_doc[chunk.document_id].append(chunk)
    docs = sorted(by_doc)
    rng.shuffle(docs)
    queues = {doc: rng.sample(by_doc[doc], len(by_doc[doc])) for doc in docs}
    sampled: list[Chunk] = []
    while len(sampled) < n and any(queues.values()):
        for doc in docs:
            if queues[doc] and len(sampled) < n:
                sampled.append(queues[doc].pop())
    return sampled


def target_categories(n: int, unanswerable_ratio: float, seed: int = 0) -> list[str]:
    """Cycle answerable categories, then sprinkle the unanswerable share at seeded positions."""
    n_unanswerable = round(n * unanswerable_ratio)
    targets = [ANSWERABLE_CATEGORIES[i % len(ANSWERABLE_CATEGORIES)] for i in range(n)]
    rng = random.Random(seed)  # noqa: S311 - sampling, not security
    for index in rng.sample(range(n), min(n_unanswerable, n)):
        targets[index] = "unanswerable"
    return targets


def build_candidate_message(chunk: Chunk, target: str) -> str:
    meta = ChunkMetadata.from_chunk(chunk)
    return (
        f"<target_category>{target}</target_category>\n\n"
        f'<passage document="{meta.doc_title}" section="{meta.section_path}">\n'
        f"{chunk.content}\n</passage>"
    )


async def generate_candidates(
    chunks: Sequence[Chunk],
    n: int,
    provider: LLMProvider,
    model: str,
    taxonomy: Taxonomy,
    prompt_version: str = "generate_candidates_v1",
    unanswerable_ratio: float = 0.15,
    seed: int = 0,
    batch_id: str | None = None,
) -> list[Candidate]:
    """Write ``n`` candidates; items the model cannot format even after repair are skipped."""
    system = load_prompt(prompt_version).replace("{taxonomy}", taxonomy.describe())
    sampled = stratified_sample(chunks, n, seed)
    targets = target_categories(len(sampled), unanswerable_ratio, seed)
    batch_id = batch_id or utc_now_iso().replace(":", "").replace("-", "")
    candidates: list[Candidate] = []
    for index, (chunk, target) in enumerate(zip(sampled, targets, strict=True)):
        request = CompletionRequest.single_turn(
            model=model,
            system=system,
            user=build_candidate_message(chunk, target),
            purpose="candidate",
        )
        try:
            output, result = await complete_structured(provider, request, CandidateOutput)
        except StructuredOutputError as exc:
            log.warning("candidate_skipped", chunk_id=chunk.id, error=str(exc))
            continue
        meta = ChunkMetadata.from_chunk(chunk)
        category = output.category
        if target == "unanswerable":
            category = "unanswerable"
        elif category == "unanswerable":
            # The model may not turn an answerable target into unanswerable.
            category = cast("Category", target)
        candidates.append(
            Candidate(
                id=f"cand-{batch_id}-{index:04d}",
                question=output.question,
                reference_answer=output.reference_answer,
                category=category,
                difficulty=output.difficulty,
                answerable=category != "unanswerable",
                target_category=target,
                source=CandidateSource(
                    chunk_id=chunk.id,
                    doc_id=chunk.document_id,
                    doc_title=meta.doc_title,
                    section_path=meta.section_path,
                    text=chunk.content,
                ),
                model=result.model,
                prompt_version=prompt_version,
                created_at=utc_now_iso(),
            )
        )
    return candidates


def write_candidates(path: Path, candidates: Sequence[Candidate]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for candidate in candidates:
            handle.write(candidate.model_dump_json() + "\n")


def read_candidates(path: Path) -> list[Candidate]:
    with path.open(encoding="utf-8") as handle:
        return [Candidate.model_validate_json(line) for line in handle if line.strip()]
