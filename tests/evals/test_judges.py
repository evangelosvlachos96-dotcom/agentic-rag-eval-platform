"""Tests for the LLM judges with mocked responses (parsing, validation, repair)."""

from __future__ import annotations

import json

import pytest

from ragplatform.evals.judges import (
    FaithfulnessVerdict,
    judge_correctness,
    judge_faithfulness,
    judge_relevance,
)
from ragplatform.llm.fake import FakeProvider
from ragplatform.llm.structured import StructuredOutputError
from ragplatform.models import Chunk, RetrievedChunk
from ragplatform.pipelines.run_config import JudgeConfig

CONFIG = JudgeConfig(max_tokens=512)
CONTEXT = [
    RetrievedChunk(
        chunk=Chunk(
            id="c1",
            document_id="d",
            content="Frames start with a four byte length.",
            index=0,
            metadata={
                "doc_title": "WTP",
                "section_path": "Framing",
                "char_start": 0,
                "char_end": 10,
                "token_count": 3,
            },
        ),
        score=1.0,
        rank=1,
        retriever="bm25",
    )
]


async def test_faithfulness_scores_supported_over_total() -> None:
    reply = json.dumps(
        {
            "claims": [
                {"claim": "a", "evidence": "e", "reasoning": "r", "supported": True},
                {"claim": "b", "evidence": "none", "reasoning": "r", "supported": False},
                {"claim": "c", "evidence": "e", "reasoning": "r", "supported": True},
            ]
        }
    )
    provider = FakeProvider(responses=[reply], model_name="judge-1")
    verdict, result = await judge_faithfulness(provider, CONFIG, "judge-1", "q", "ans", CONTEXT)
    assert verdict.score == pytest.approx(2 / 3)
    assert result.model == "judge-1"
    request = provider.requests[0]
    assert request.purpose == "judge_faithfulness"
    assert request.max_tokens == 512
    assert '<chunk id="c1"' in request.messages[0].content
    assert "<answer>\nans\n</answer>" in request.messages[0].content
    assert "atomic" in request.system.lower()


def test_faithfulness_with_no_claims_has_no_score() -> None:
    assert FaithfulnessVerdict(claims=[]).score is None


async def test_correctness_and_relevance_parse_and_carry_reasoning() -> None:
    provider = FakeProvider(
        responses=[
            json.dumps({"evidence": "ref says X", "reasoning": "matches", "correct": True}),
            json.dumps({"reasoning": "on topic", "relevant": False}),
        ]
    )
    correctness, _ = await judge_correctness(provider, CONFIG, "m", "q", "ans", "ref")
    relevance, _ = await judge_relevance(provider, CONFIG, "m", "q", "ans")
    assert correctness.correct is True
    assert correctness.reasoning == "matches"
    assert relevance.relevant is False
    assert (
        "<reference_answer>\nref\n</reference_answer>" in provider.requests[0].messages[0].content
    )
    assert provider.requests[0].purpose == "judge_correctness"
    assert provider.requests[1].purpose == "judge_relevance"


async def test_invalid_judge_output_is_repaired_once_then_fails() -> None:
    provider = FakeProvider(
        responses=["not json", json.dumps({"reasoning": "ok", "relevant": True})]
    )
    verdict, result = await judge_relevance(provider, CONFIG, "m", "q", "a")
    assert verdict.relevant is True
    assert result.repaired is True

    failing = FakeProvider(responses=['{"relevant": "maybe"}', '{"wrong": 1}'])
    with pytest.raises(StructuredOutputError):
        await judge_relevance(failing, CONFIG, "m", "q", "a")
