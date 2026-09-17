"""A disk cache in front of any provider.

The key is the sha256 of the full :class:`CompletionRequest` (model, system,
messages, max_tokens, purpose), so an identical call is served
from ``<cache_dir>/<key>.json`` without touching the network. Evaluation runs
therefore cost nothing to repeat, and a run can be resumed after a crash.
Hits and misses are counted so the runner can report them.
"""

from __future__ import annotations

import hashlib
from typing import TYPE_CHECKING

import structlog

from ragplatform.llm.provider import CompletionRequest, CompletionResponse

if TYPE_CHECKING:
    from pathlib import Path

    from ragplatform.llm.provider import LLMProvider

log = structlog.get_logger(__name__)


def cache_key(request: CompletionRequest) -> str:
    payload = request.model_dump_json()  # field order is fixed by the model definition
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


class CachedProvider:
    """Wraps ``inner`` with a content-addressed JSON file cache."""

    def __init__(self, inner: LLMProvider, cache_dir: Path) -> None:
        self._inner = inner
        self._dir = cache_dir
        self.hits = 0
        self.misses = 0

    @property
    def name(self) -> str:
        return f"cached({self._inner.name})"

    def _path(self, request: CompletionRequest) -> Path:
        return self._dir / f"{cache_key(request)}.json"

    async def complete(self, request: CompletionRequest) -> CompletionResponse:
        path = self._path(request)
        if path.exists():
            self.hits += 1
            stored = CompletionResponse.model_validate_json(path.read_text(encoding="utf-8"))
            return stored.model_copy(update={"cached": True})
        self.misses += 1
        response = await self._inner.complete(request)
        self._dir.mkdir(parents=True, exist_ok=True)
        path.write_text(response.model_dump_json(indent=2), encoding="utf-8")
        log.debug("llm_cache_store", purpose=request.purpose, key=path.stem[:12])
        return response
