"""Duplicate chunk removal: exact matches by hash, near matches by MinHash LSH.

Exact duplicates are detected with a sha256 over whitespace-normalized,
lower-cased text. Near duplicates use MinHash signatures over word 3-shingles
and a locality-sensitive-hash index (``datasketch``), so that each chunk is only
compared against likely candidates rather than every other chunk. Chunks are
processed in corpus order and the first occurrence is kept, which makes the
result deterministic.
"""

from __future__ import annotations

import hashlib
import re
from typing import TYPE_CHECKING

import structlog
from datasketch import MinHash, MinHashLSH
from pydantic import BaseModel, ConfigDict, Field

if TYPE_CHECKING:
    from ragplatform.models import Chunk

log = structlog.get_logger(__name__)

_WORD = re.compile(r"\w+")


class DedupConfig(BaseModel):
    """Near-duplicate parameters. Part of the dataset version hash."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    threshold: float = Field(
        default=0.85, gt=0.0, le=1.0, description="Estimated Jaccard above which chunks match."
    )
    num_perm: int = Field(default=128, ge=16, description="MinHash permutations.")
    shingle_size: int = Field(default=3, ge=1, description="Words per shingle.")


class RemovedChunk(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    chunk_id: str
    duplicate_of: str
    kind: str = Field(description="'exact' or 'near'.")


class DedupReport(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    kept: int
    exact_removed: int
    near_removed: int
    removed: list[RemovedChunk] = Field(default_factory=list)


def _normalized_words(text: str) -> list[str]:
    return _WORD.findall(text.lower())


def _exact_key(words: list[str]) -> str:
    return hashlib.sha256(" ".join(words).encode("utf-8")).hexdigest()


def _shingles(words: list[str], size: int) -> set[str]:
    if len(words) <= size:
        return {" ".join(words)}
    return {" ".join(words[i : i + size]) for i in range(len(words) - size + 1)}


def _minhash(words: list[str], config: DedupConfig) -> MinHash:
    signature = MinHash(num_perm=config.num_perm)
    for shingle in _shingles(words, config.shingle_size):
        signature.update(shingle.encode("utf-8"))
    return signature


def dedup_chunks(
    chunks: list[Chunk], config: DedupConfig | None = None
) -> tuple[list[Chunk], DedupReport]:
    """Return the chunks to keep plus a report of what was removed and why."""
    config = config or DedupConfig()
    lsh = MinHashLSH(threshold=config.threshold, num_perm=config.num_perm)
    seen_exact: dict[str, str] = {}
    kept: list[Chunk] = []
    removed: list[RemovedChunk] = []

    for chunk in chunks:
        words = _normalized_words(chunk.content)
        key = _exact_key(words)
        if key in seen_exact:
            removed.append(
                RemovedChunk(chunk_id=chunk.id, duplicate_of=seen_exact[key], kind="exact")
            )
            continue
        signature = _minhash(words, config)
        candidates = lsh.query(signature)
        if candidates:
            removed.append(
                RemovedChunk(chunk_id=chunk.id, duplicate_of=sorted(candidates)[0], kind="near")
            )
            continue
        seen_exact[key] = chunk.id
        lsh.insert(chunk.id, signature)
        kept.append(chunk)

    report = DedupReport(
        kept=len(kept),
        exact_removed=sum(1 for r in removed if r.kind == "exact"),
        near_removed=sum(1 for r in removed if r.kind == "near"),
        removed=removed,
    )
    log.info(
        "dedup_complete",
        kept=report.kept,
        exact_removed=report.exact_removed,
        near_removed=report.near_removed,
    )
    return kept, report
