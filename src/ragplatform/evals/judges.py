"""LLM judges: faithfulness, correctness and answer relevance.

Design choices that mitigate known judge biases:

- **Versioned prompts** (``judge_*_v1``) recorded in every run.
- **Evidence and reasoning before the verdict**: the JSON field order forces
  the model to quote and argue before it decides.
- **Rubric, not opinion**: correctness is graded against a human reference
  answer with an explicit three-part rubric; relevance and faithfulness are
  binary per claim, so verbosity earns nothing.
- **Faithfulness is claim-level**: the answer is split into atomic claims and
  each is judged against the retrieved context only. Score = supported / total.
- **Separate judge model** (``JudgeConfig.model`` or ``Settings.anthropic_judge_model``),
  so the generator is not grading itself.
- **Validated JSON with one repair retry** via :func:`complete_structured`.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import BaseModel, ConfigDict, Field

from ragplatform.generation.generator import format_context
from ragplatform.llm.provider import CompletionRequest
from ragplatform.llm.structured import StructuredResult, complete_structured
from ragplatform.prompts import load_prompt

if TYPE_CHECKING:
    from collections.abc import Sequence

    from ragplatform.llm.provider import LLMProvider
    from ragplatform.models import RetrievedChunk
    from ragplatform.pipelines.run_config import JudgeConfig


class ClaimVerdict(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    claim: str
    evidence: str
    reasoning: str
    supported: bool


class FaithfulnessVerdict(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    claims: list[ClaimVerdict] = Field(default_factory=list)

    @property
    def score(self) -> float | None:
        """Supported / total claims; None when the answer made no checkable claims."""
        if not self.claims:
            return None
        return sum(1 for c in self.claims if c.supported) / len(self.claims)


class CorrectnessVerdict(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    evidence: str
    reasoning: str
    correct: bool


class RelevanceVerdict(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    reasoning: str
    relevant: bool


def _request(
    config: JudgeConfig, model: str, prompt_name: str, user: str, purpose: str
) -> CompletionRequest:
    return CompletionRequest.single_turn(
        model=model,
        system=load_prompt(prompt_name),
        user=user,
        purpose=purpose,
        max_tokens=config.max_tokens,
    )


async def judge_faithfulness(
    provider: LLMProvider,
    config: JudgeConfig,
    model: str,
    question: str,
    answer_text: str,
    context: Sequence[RetrievedChunk],
) -> tuple[FaithfulnessVerdict, StructuredResult]:
    user = (
        f"<question>\n{question}\n</question>\n\n"
        f"<context>\n{format_context(context)}\n</context>\n\n"
        f"<answer>\n{answer_text}\n</answer>"
    )
    request = _request(config, model, config.faithfulness_prompt, user, "judge_faithfulness")
    return await complete_structured(provider, request, FaithfulnessVerdict)


async def judge_correctness(
    provider: LLMProvider,
    config: JudgeConfig,
    model: str,
    question: str,
    answer_text: str,
    reference_answer: str,
) -> tuple[CorrectnessVerdict, StructuredResult]:
    user = (
        f"<question>\n{question}\n</question>\n\n"
        f"<reference_answer>\n{reference_answer}\n</reference_answer>\n\n"
        f"<candidate_answer>\n{answer_text}\n</candidate_answer>"
    )
    request = _request(config, model, config.correctness_prompt, user, "judge_correctness")
    return await complete_structured(provider, request, CorrectnessVerdict)


async def judge_relevance(
    provider: LLMProvider,
    config: JudgeConfig,
    model: str,
    question: str,
    answer_text: str,
) -> tuple[RelevanceVerdict, StructuredResult]:
    user = f"<question>\n{question}\n</question>\n\n<answer>\n{answer_text}\n</answer>"
    request = _request(config, model, config.relevance_prompt, user, "judge_relevance")
    return await complete_structured(provider, request, RelevanceVerdict)
