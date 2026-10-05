"""Bounded async jobs with opt-in transient retries and stable output ordering."""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable, Sequence

T = TypeVar("T")
R = TypeVar("R")


class RetryableError(RuntimeError):
    """Only explicitly classified transient failures are retried."""


class BatchConfig(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    concurrency: int = Field(default=4, ge=1, le=64)
    max_attempts: int = Field(default=1, ge=1, le=5)
    timeout_seconds: float = Field(default=60, gt=0)
    backoff_seconds: float = Field(default=0.25, ge=0, le=30)


class BatchResult(BaseModel, Generic[R]):
    model_config = ConfigDict(frozen=True, extra="forbid")

    index: int
    attempts: int
    value: R | None = None
    error: str | None = None


async def run_batch(
    items: Sequence[T],
    worker: Callable[[T], Awaitable[R]],
    *,
    config: BatchConfig | None = None,
) -> list[BatchResult[R]]:
    """Limit active jobs and tasks to worker count. Cancellation propagates.

    RetryableError is an explicit caller choice: retries may repeat external
    effects or paid calls. Timeouts and other exceptions are not retried.
    """
    config = config or BatchConfig()
    pending = iter(enumerate(items))
    results: list[BatchResult[R] | None] = [None] * len(items)

    async def consume() -> None:
        for index, item in pending:
            for attempt in range(1, config.max_attempts + 1):
                try:
                    value = await asyncio.wait_for(worker(item), config.timeout_seconds)
                    results[index] = BatchResult(index=index, attempts=attempt, value=value)
                    break
                except RetryableError:
                    if attempt == config.max_attempts:
                        results[index] = BatchResult(
                            index=index, attempts=attempt, error="RetryableError"
                        )
                    else:
                        await asyncio.sleep(config.backoff_seconds * 2 ** (attempt - 1))
                except Exception as exc:
                    results[index] = BatchResult(
                        index=index, attempts=attempt, error=type(exc).__name__
                    )
                    break

    async with asyncio.TaskGroup() as group:
        for _ in range(min(config.concurrency, len(items))):
            group.create_task(consume())
    if any(result is None for result in results):
        raise asyncio.CancelledError("Batch worker cancelled")
    return [result for result in results if result is not None]
