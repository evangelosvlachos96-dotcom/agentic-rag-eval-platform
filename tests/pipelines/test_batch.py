"""Batch ordering, concurrency, retry boundaries and cancellation."""

import asyncio

import pytest

from ragplatform.pipelines.batch import BatchConfig, RetryableError, run_batch


@pytest.mark.asyncio
async def test_concurrency_order_and_explicit_retry() -> None:
    active = 0
    peak = 0
    attempts: dict[int, int] = {}

    async def worker(value: int) -> int:
        nonlocal active, peak
        active += 1
        peak = max(peak, active)
        try:
            await asyncio.sleep(0.001)
            attempts[value] = attempts.get(value, 0) + 1
            if value == 1 and attempts[value] == 1:
                raise RetryableError("temporary")
            return value * 2
        finally:
            active -= 1

    results = await run_batch(
        list(range(10)),
        worker,
        config=BatchConfig(concurrency=2, max_attempts=2, backoff_seconds=0),
    )
    assert [r.value for r in results] == list(range(0, 20, 2))
    assert results[1].attempts == 2
    assert peak == 2


@pytest.mark.asyncio
async def test_permanent_errors_and_timeout_are_not_retried() -> None:
    async def worker(value: int) -> int:
        if value == 0:
            raise ValueError("invalid")
        await asyncio.sleep(10)
        return value

    results = await run_batch(
        [0, 1], worker, config=BatchConfig(max_attempts=3, timeout_seconds=0.01)
    )
    assert [r.error for r in results] == ["ValueError", "TimeoutError"]
    assert all(r.attempts == 1 for r in results)
    assert await run_batch([], worker) == []


@pytest.mark.asyncio
async def test_cancellation_propagates() -> None:
    async def worker(value: int) -> int:
        raise asyncio.CancelledError

    # A child cancellation produces no result; it must not be reported as success.
    with pytest.raises(asyncio.CancelledError):
        await run_batch([1], worker)
