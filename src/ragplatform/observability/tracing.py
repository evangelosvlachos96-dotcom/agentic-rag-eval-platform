"""Lightweight correlated spans; logs contain timings, never prompts or secrets."""

from __future__ import annotations

from contextlib import contextmanager
from contextvars import ContextVar
from time import perf_counter
from typing import TYPE_CHECKING
from uuid import uuid4

import structlog

if TYPE_CHECKING:
    from collections.abc import Iterator

trace_id: ContextVar[str | None] = ContextVar("trace_id", default=None)
log = structlog.get_logger(__name__)


@contextmanager
def trace() -> Iterator[str]:
    value = uuid4().hex
    token = trace_id.set(value)
    try:
        yield value
    finally:
        trace_id.reset(token)


@contextmanager
def span(name: str) -> Iterator[None]:
    started = perf_counter()
    error = None
    try:
        yield
    except BaseException as exc:
        error = type(exc).__name__
        raise
    finally:
        log.info(
            "span",
            trace_id=trace_id.get(),
            name=name,
            duration_ms=round((perf_counter() - started) * 1000, 3),
            error=error,
        )
