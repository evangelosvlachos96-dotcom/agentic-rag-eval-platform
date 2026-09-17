"""Tests for candidate generation: stratified sampling and the mocked LLM path."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from ragplatform.evals.candidates import (
    generate_candidates,
    read_candidates,
    stratified_sample,
    target_categories,
    write_candidates,
)
from ragplatform.evals.taxonomy import load_taxonomy
from ragplatform.ingestion.chunking import chunk_document
from ragplatform.ingestion.loaders import load_file
from ragplatform.llm.fake import FakeProvider, mock_responder
from ragplatform.models import Chunk

if TYPE_CHECKING:
    from ragplatform.llm.provider import CompletionRequest

TAXONOMY_PATH = Path(__file__).resolve().parents[2] / "eval_sets" / "taxonomy_v1.yaml"


def _chunk(doc: str, i: int) -> Chunk:
    return Chunk(
        id=f"{doc}-{i:04d}",
        document_id=doc,
        content=f"text {doc} {i}",
        index=i,
        metadata={
            "doc_title": doc,
            "section_path": "S",
            "char_start": 0,
            "char_end": 1,
            "token_count": 1,
        },
    )


def test_stratified_sample_round_robins_across_documents() -> None:
    chunks = [_chunk("a", i) for i in range(10)] + [_chunk("b", i) for i in range(2)]
    chunks += [_chunk("c", i) for i in range(5)]
    sampled = stratified_sample(chunks, 6, seed=1)
    counts = Counter(c.document_id for c in sampled)
    assert len(sampled) == 6
    assert counts == {"a": 2, "b": 2, "c": 2}
    assert stratified_sample(chunks, 6, seed=1) == sampled  # seeded => reproducible
    assert len(stratified_sample(chunks, 100, seed=1)) == 17  # capped at corpus size
    assert stratified_sample([], 5) == []


def test_target_categories_cycle_and_include_unanswerable_share() -> None:
    targets = target_categories(20, unanswerable_ratio=0.15, seed=0)
    assert len(targets) == 20
    assert targets.count("unanswerable") == 3
    assert set(targets) - {"unanswerable"} == {
        "lookup",
        "conceptual",
        "exact_term",
        "multi_hop",
        "comparison",
    }
    assert target_categories(20, 0.15, seed=0) == targets
    assert target_categories(0, 0.5) == []


async def test_generate_candidates_with_mocked_llm(
    fixture_corpus_dir: Path, tmp_path: Path
) -> None:
    chunks: list[Chunk] = []
    for path in sorted(fixture_corpus_dir.iterdir()):
        chunks.extend(chunk_document(load_file(path)))
    provider = FakeProvider(responder=mock_responder)
    taxonomy = load_taxonomy(TAXONOMY_PATH)
    candidates = await generate_candidates(
        chunks, 6, provider, "fake-model", taxonomy, unanswerable_ratio=0.34, seed=0, batch_id="t"
    )
    assert len(candidates) == 6
    assert provider.calls == 6
    assert [c.id for c in candidates] == [f"cand-t-{i:04d}" for i in range(6)]
    unanswerable = [c for c in candidates if c.target_category == "unanswerable"]
    assert len(unanswerable) == 2
    assert all(c.category == "unanswerable" and not c.answerable for c in unanswerable)
    answerable = [c for c in candidates if c.target_category != "unanswerable"]
    assert all(c.answerable for c in answerable)
    first = candidates[0]
    assert first.source.text == next(c for c in chunks if c.id == first.source.chunk_id).content
    assert first.prompt_version == "generate_candidates_v1"
    system = provider.requests[0].system
    assert "lookup:" in system  # taxonomy rendered into the prompt
    assert "<target_category>" in provider.requests[0].messages[0].content

    out = tmp_path / "cands.jsonl"
    write_candidates(out, candidates)
    assert read_candidates(out) == candidates


async def test_unrepairable_candidate_is_skipped() -> None:
    def responder(request: CompletionRequest) -> str:
        if request.purpose.startswith("candidate"):
            return "garbage"
        raise AssertionError("unexpected purpose")

    chunks = [_chunk("a", 0)]
    taxonomy = load_taxonomy(TAXONOMY_PATH)
    result = await generate_candidates(chunks, 1, FakeProvider(responder=responder), "m", taxonomy)
    assert result == []


async def test_answerable_target_cannot_become_unanswerable() -> None:
    reply = json.dumps(
        {
            "question": "q?",
            "reference_answer": "a",
            "category": "unanswerable",
            "difficulty": "easy",
        }
    )
    taxonomy = load_taxonomy(TAXONOMY_PATH)
    result = await generate_candidates(
        [_chunk("a", 0)], 1, FakeProvider(responses=[reply]), "m", taxonomy, unanswerable_ratio=0.0
    )
    assert result[0].target_category == "lookup"
    assert result[0].category == "lookup"
    assert result[0].answerable is True


def test_taxonomy_file_matches_schema() -> None:
    taxonomy = load_taxonomy(TAXONOMY_PATH)
    assert taxonomy.version == "v1"
    assert set(taxonomy.categories) == {
        "lookup",
        "conceptual",
        "exact_term",
        "multi_hop",
        "comparison",
        "unanswerable",
    }
    with pytest.raises(ValueError, match="must equal"):
        taxonomy.model_validate({"version": "x", "categories": {}})
