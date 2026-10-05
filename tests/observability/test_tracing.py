"""Correlation contexts restore correctly and isolate concurrent tasks."""

import asyncio

import pytest

from ragplatform.observability.tracing import span, trace, trace_id


@pytest.mark.asyncio
async def test_trace_context_isolation() -> None:
    async def task() -> str:
        with trace() as value, span("test"):
            await asyncio.sleep(0)
            assert trace_id.get() == value
            return value

    values = await asyncio.gather(task(), task())
    assert values[0] != values[1]
    assert trace_id.get() is None
