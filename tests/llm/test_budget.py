from pathlib import Path

import pytest

from ragplatform.llm.budget import BudgetedProvider, BudgetStoppedError
from ragplatform.llm.pricing import ModelPrice, Pricing
from ragplatform.llm.provider import CompletionRequest, CompletionResponse, LLMError
from ragplatform.models import TokenUsage


class CountedFake:
    name = "fake"
    calls = 0
    fail = False

    async def count_input_tokens(self, request: CompletionRequest) -> int:
        return 100

    async def complete(self, request: CompletionRequest) -> CompletionResponse:
        self.calls += 1
        if self.fail:
            raise LLMError("simulated failure")
        return CompletionResponse(
            text="ok", model=request.model, usage=TokenUsage(input_tokens=100, output_tokens=10)
        )


def setup(tmp_path: Path, rate: float = 1) -> tuple[CountedFake, BudgetedProvider]:
    fake = CountedFake()
    pricing = Pricing(
        checked_on="2026-10-10",
        source="test",
        models={"test": ModelPrice(input_per_mtok=rate, output_per_mtok=rate)},
    )
    return fake, BudgetedProvider(fake, pricing, tmp_path / "budget.json")


def request() -> CompletionRequest:
    return CompletionRequest.single_turn(
        model="test", system="", user="hello", purpose="test", max_tokens=100
    )


@pytest.mark.asyncio
async def test_reconciles_and_reloads_actual_usage(tmp_path: Path) -> None:
    fake, guard = setup(tmp_path)
    await guard.complete(request())
    assert fake.calls == 1
    assert guard.ledger.committed_usd == pytest.approx(0.00011)
    loaded = BudgetedProvider(fake, guard.pricing, guard.path)
    assert loaded.ledger == guard.ledger


@pytest.mark.asyncio
async def test_refuses_maximum_allowance_before_dispatch(tmp_path: Path) -> None:
    fake, guard = setup(tmp_path, rate=3000)
    with pytest.raises(BudgetStoppedError):
        await guard.complete(request())
    assert fake.calls == 0


@pytest.mark.asyncio
async def test_failed_call_retains_reservation_and_stops_across_restart(tmp_path: Path) -> None:
    fake, guard = setup(tmp_path)
    fake.fail = True
    with pytest.raises(LLMError):
        await guard.complete(request())
    assert guard.ledger.committed_usd > 0
    loaded = BudgetedProvider(fake, guard.pricing, guard.path)
    with pytest.raises(BudgetStoppedError):
        await loaded.complete(request())
    assert fake.calls == 1


@pytest.mark.asyncio
async def test_unknown_price_never_dispatches(tmp_path: Path) -> None:
    fake, guard = setup(tmp_path)
    with pytest.raises(KeyError):
        await guard.complete(request().model_copy(update={"model": "unknown"}))
    assert fake.calls == 0


@pytest.mark.asyncio
async def test_reservation_persisted_before_provider_call(tmp_path: Path) -> None:
    class ObservedFake(CountedFake):
        async def complete(self, request: CompletionRequest) -> CompletionResponse:
            saved = (tmp_path / "budget.json").read_text()
            assert '"status": "reserved"' in saved
            return await super().complete(request)

    _, guard = setup(tmp_path)
    guard.provider = ObservedFake()
    await guard.complete(request())


@pytest.mark.asyncio
async def test_underestimated_reservation_stops_next_request(tmp_path: Path) -> None:
    class LargeUsageFake(CountedFake):
        async def complete(self, request: CompletionRequest) -> CompletionResponse:
            self.calls += 1
            return CompletionResponse(
                text="ok",
                model=request.model,
                usage=TokenUsage(input_tokens=5000, output_tokens=10),
            )

    _, guard = setup(tmp_path)
    fake = LargeUsageFake()
    guard.provider = fake
    await guard.complete(request())
    with pytest.raises(BudgetStoppedError):
        await guard.complete(request())
    assert fake.calls == 1
    assert guard.ledger.records[0].status == "reservation_exceeded"
