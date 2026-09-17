"""Estimate the LLM calls, tokens and cost of a generation run before it starts.

The estimate builds the real answer prompts (retrieval has already run) and
counts them with the approximate token counter, then adds a fixed allowance
per judge call. It is deliberately an over-estimate: judges are budgeted as
if every item is answered, even though abstentions skip some judge calls.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import BaseModel, ConfigDict, Field

from ragplatform.generation.generator import build_user_message
from ragplatform.ingestion.tokens import ApproxTokenCounter
from ragplatform.models import TokenUsage
from ragplatform.prompts import load_prompt

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence

    from ragplatform.evals.models import EvalItem
    from ragplatform.llm.pricing import Pricing
    from ragplatform.models import RetrievedChunk
    from ragplatform.pipelines.run_config import RunConfig

ANSWER_OUTPUT_TOKENS = 250
JUDGE_OUTPUT_TOKENS = {"faithfulness": 500, "correctness": 250, "relevance": 120}


class CostEstimate(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    n_items: int
    n_llm_calls: int
    generator_model: str
    judge_model: str
    generator_usage: TokenUsage
    judge_usage: TokenUsage
    cost_usd: float | None = Field(description="None when a model has no price entry.")

    @property
    def total_usage(self) -> TokenUsage:
        return self.generator_usage + self.judge_usage


def estimate_generation_run(
    items: Sequence[EvalItem],
    retrievals: Mapping[str, Sequence[RetrievedChunk]],
    config: RunConfig,
    generator_model: str,
    judge_model: str,
    pricing: Pricing | None,
) -> CostEstimate:
    counter = ApproxTokenCounter()
    answer_system = counter.count(load_prompt(config.generation.prompt_version))
    judge_systems = {
        "faithfulness": counter.count(load_prompt(config.judge.faithfulness_prompt)),
        "correctness": counter.count(load_prompt(config.judge.correctness_prompt)),
        "relevance": counter.count(load_prompt(config.judge.relevance_prompt)),
    }
    gen_in = gen_out = judge_in = judge_out = 0
    calls = 0
    for item in items:
        chunks = retrievals.get(item.id, [])
        if not chunks:
            continue  # empty retrieval abstains without any LLM call
        context_tokens = counter.count(build_user_message(item.question, chunks))
        calls += 1
        gen_in += answer_system + context_tokens
        gen_out += ANSWER_OUTPUT_TOKENS
        # faithfulness sees the context again plus the answer; relevance sees only q + a.
        calls += 2
        judge_in += judge_systems["faithfulness"] + context_tokens + ANSWER_OUTPUT_TOKENS
        judge_out += JUDGE_OUTPUT_TOKENS["faithfulness"]
        judge_in += judge_systems["relevance"] + counter.count(item.question) + ANSWER_OUTPUT_TOKENS
        judge_out += JUDGE_OUTPUT_TOKENS["relevance"]
        if item.answerable:
            calls += 1
            judge_in += (
                judge_systems["correctness"]
                + counter.count(item.question)
                + counter.count(item.reference_answer)
                + ANSWER_OUTPUT_TOKENS
            )
            judge_out += JUDGE_OUTPUT_TOKENS["correctness"]

    generator_usage = TokenUsage(input_tokens=gen_in, output_tokens=gen_out)
    judge_usage = TokenUsage(input_tokens=judge_in, output_tokens=judge_out)
    cost: float | None = None
    if pricing is not None:
        try:
            cost = pricing.cost_usd(generator_model, generator_usage) + pricing.cost_usd(
                judge_model, judge_usage
            )
        except KeyError:
            cost = None
    return CostEstimate(
        n_items=len(items),
        n_llm_calls=calls,
        generator_model=generator_model,
        judge_model=judge_model,
        generator_usage=generator_usage,
        judge_usage=judge_usage,
        cost_usd=cost,
    )
