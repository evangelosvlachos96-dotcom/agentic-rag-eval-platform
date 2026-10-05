"""Prepare an approximate candidate cost estimate without constructing a provider."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ragplatform.evals.candidates import (
    build_candidate_message,
    stratified_sample,
    target_categories,
)
from ragplatform.ingestion.tokens import ApproxTokenCounter
from ragplatform.models import TokenUsage
from ragplatform.prompts import load_prompt

if TYPE_CHECKING:
    from collections.abc import Sequence

    from ragplatform.evals.taxonomy import Taxonomy
    from ragplatform.models import Chunk


def candidate_usage(
    chunks: Sequence[Chunk], n: int, taxonomy: Taxonomy, ratio: float, seed: int
) -> TokenUsage:
    """Allow full output limits and one repair per candidate; token counts are approximate."""
    sampled = stratified_sample(chunks, n, seed)
    targets = target_categories(len(sampled), ratio, seed)
    counter = ApproxTokenCounter()
    system = load_prompt("generate_candidates_v1").replace("{taxonomy}", taxonomy.describe())
    initial = sum(
        counter.count(system) + counter.count(build_candidate_message(chunk, target))
        for chunk, target in zip(sampled, targets, strict=True)
    )
    return TokenUsage(
        input_tokens=2 * initial + len(sampled) * (4096 + 1000),
        output_tokens=len(sampled) * 4096 * 2,
    )
