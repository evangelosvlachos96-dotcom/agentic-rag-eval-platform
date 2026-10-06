"""Accounting at the provider boundary, independent of real pricing or API keys."""

from pathlib import Path

import pytest

from ragplatform.llm.cache import CachedProvider
from ragplatform.llm.fake import FakeProvider
from ragplatform.llm.metering import MeteredProvider
from ragplatform.llm.pricing import ModelPrice, Pricing
from ragplatform.llm.provider import CompletionRequest, LLMError


def request(model: str) -> CompletionRequest:
    return CompletionRequest.single_turn(model=model, system="a" * 40, user="q", purpose="test")


def pricing() -> Pricing:
    return Pricing(
        checked_on="test",
        source="Synthetic test rates, not actual prices",
        models={
            "generator": ModelPrice(input_per_mtok=1, output_per_mtok=2),
            "judge": ModelPrice(input_per_mtok=3, output_per_mtok=4),
        },
    )


@pytest.mark.asyncio
async def test_prices_each_model_and_excludes_cached_usage(tmp_path: Path) -> None:
    fake = FakeProvider(responses=["a" * 40, "b" * 40])
    meter = MeteredProvider(CachedProvider(fake, tmp_path / "cache"))
    await meter.complete(request("generator"))
    await meter.complete(request("judge"))
    await meter.complete(request("generator"))
    assert fake.calls == 2
    assert len(meter.records) == 3
    assert meter.usage_by_model()["generator"].input_tokens == 20
    assert meter.usage_by_model(billable_only=True)["generator"].input_tokens == 10
    assert meter.estimated_cost(pricing()) == pytest.approx(100 / 1_000_000)
    replay = MeteredProvider(CachedProvider(FakeProvider(responses=[]), tmp_path / "cache"))
    await replay.complete(request("generator"))
    assert replay.estimated_cost(None) == 0


@pytest.mark.asyncio
async def test_failures_and_unknown_prices_never_report_zero_cost() -> None:
    meter = MeteredProvider(FakeProvider(responses=["not json"]))
    await meter.complete(request("unknown-model"))
    assert meter.estimated_cost(pricing()) is None
    assert meter.records[0].usage is not None  # parsing failure still consumed tokens
    with pytest.raises(LLMError, match="no responses"):
        await meter.complete(request("generator"))
    assert len(meter.records) == 2
    assert meter.records[1].usage is None
    assert meter.estimated_cost(pricing()) is None
