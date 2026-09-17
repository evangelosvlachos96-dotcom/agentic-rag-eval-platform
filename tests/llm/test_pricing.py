"""Tests for ragplatform.llm.pricing and the shipped configs/pricing.yaml."""

from __future__ import annotations

from pathlib import Path

import pytest

from ragplatform.llm.pricing import ModelPrice, Pricing, load_pricing
from ragplatform.models import TokenUsage

PRICING_PATH = Path(__file__).resolve().parents[2] / "configs" / "pricing.yaml"


def test_shipped_pricing_file_loads_and_covers_default_models() -> None:
    pricing = load_pricing(PRICING_PATH)
    assert {"claude-opus-5", "claude-sonnet-5", "fake-model"} <= set(pricing.models)
    assert pricing.checked_on
    assert pricing.cost_usd("fake-model", TokenUsage(input_tokens=10_000, output_tokens=10)) == 0


def test_cost_is_linear_in_tokens() -> None:
    pricing = Pricing(
        checked_on="2026-01-01",
        source="test",
        models={"m": ModelPrice(input_per_mtok=2.0, output_per_mtok=10.0)},
    )
    usage = TokenUsage(input_tokens=1_000_000, output_tokens=100_000)
    assert pricing.cost_usd("m", usage) == pytest.approx(2.0 + 1.0)
    assert pricing.cost_usd("m", TokenUsage(input_tokens=0, output_tokens=0)) == 0.0


def test_unknown_model_raises() -> None:
    pricing = Pricing(checked_on="2026-01-01", source="test", models={})
    with pytest.raises(KeyError, match="no price"):
        pricing.price_for("mystery")


def test_token_usage_addition() -> None:
    total = TokenUsage(input_tokens=1, output_tokens=2) + TokenUsage(
        input_tokens=3, output_tokens=4
    )
    assert total == TokenUsage(input_tokens=4, output_tokens=6)
