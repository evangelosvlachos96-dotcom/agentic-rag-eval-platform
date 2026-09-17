"""Versioned processed datasets on disk.

A processed dataset lives in ``data/processed/<dataset_version>/`` and holds
``chunks.jsonl`` (one :class:`~ragplatform.models.Chunk` per line) plus
``manifest.json``. The version is a short hash of the input files' content
hashes and the chunking / dedup configuration, so re-chunking with different
parameters produces a sibling directory instead of overwriting.
"""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from pydantic import BaseModel, ConfigDict, Field

from ragplatform.ingestion.chunking import ChunkingConfig
from ragplatform.ingestion.dedup import DedupConfig
from ragplatform.models import Chunk

if TYPE_CHECKING:
    from pathlib import Path

CHUNKS_FILE = "chunks.jsonl"
MANIFEST_FILE = "manifest.json"


class SourceFile(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    path: str = Field(description="Path relative to the raw directory, POSIX style.")
    sha256: str
    size_bytes: int = Field(ge=0)


class DocumentSummary(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    doc_id: str
    title: str
    source: str | None
    n_chunks: int = Field(ge=0)


class DatasetManifest(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    dataset_version: str
    created_at: str
    source_dir: str
    source_files: list[SourceFile]
    chunking: ChunkingConfig
    dedup: DedupConfig
    n_documents: int = Field(ge=0)
    n_chunks: int = Field(ge=0)
    exact_removed: int = Field(ge=0)
    near_removed: int = Field(ge=0)
    documents: list[DocumentSummary]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def compute_dataset_version(
    source_files: list[SourceFile], chunking: ChunkingConfig, dedup: DedupConfig
) -> str:
    """Short, deterministic hash of inputs + configuration (12 hex chars)."""
    payload = {
        "files": [(f.path, f.sha256) for f in sorted(source_files, key=lambda f: f.path)],
        "chunking": chunking.model_dump(),
        "dedup": dedup.model_dump(),
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()[:12]


def utc_now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat()


def dataset_dir(processed_root: Path, dataset_version: str) -> Path:
    return processed_root / dataset_version


def write_dataset(directory: Path, chunks: list[Chunk], manifest: DatasetManifest) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    with (directory / CHUNKS_FILE).open("w", encoding="utf-8") as handle:
        for chunk in chunks:
            handle.write(chunk.model_dump_json() + "\n")
    (directory / MANIFEST_FILE).write_text(manifest.model_dump_json(indent=2), encoding="utf-8")


def read_chunks(directory: Path) -> list[Chunk]:
    path = directory / CHUNKS_FILE
    with path.open(encoding="utf-8") as handle:
        return [Chunk.model_validate_json(line) for line in handle if line.strip()]


def read_manifest(directory: Path) -> DatasetManifest:
    return DatasetManifest.model_validate_json(
        (directory / MANIFEST_FILE).read_text(encoding="utf-8")
    )


def list_dataset_versions(processed_root: Path) -> list[str]:
    """Dataset versions under ``processed_root``, newest first by creation time."""
    manifests: list[DatasetManifest] = []
    if not processed_root.exists():
        return []
    for child in processed_root.iterdir():
        if child.is_dir() and (child / MANIFEST_FILE).exists():
            manifests.append(read_manifest(child))
    manifests.sort(key=lambda m: m.created_at, reverse=True)
    return [m.dataset_version for m in manifests]
