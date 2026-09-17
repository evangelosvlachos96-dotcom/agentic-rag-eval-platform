"""Tests for ragplatform.ingestion.pipeline and dataset I/O."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from ragplatform.ingestion.chunking import ChunkingConfig
from ragplatform.ingestion.dataset import (
    SourceFile,
    compute_dataset_version,
    list_dataset_versions,
    read_chunks,
    read_manifest,
)
from ragplatform.ingestion.dedup import DedupConfig
from ragplatform.ingestion.pipeline import ingest_directory

if TYPE_CHECKING:
    from pathlib import Path


def test_ingest_fixture_corpus_writes_versioned_dataset(
    fixture_corpus_dir: Path, tmp_path: Path
) -> None:
    result = ingest_directory(
        fixture_corpus_dir, tmp_path, ChunkingConfig(), DedupConfig(threshold=0.8)
    )
    assert result.output_dir == tmp_path / result.dataset_version
    assert (result.output_dir / "chunks.jsonl").exists()
    manifest = read_manifest(result.output_dir)
    assert manifest.n_documents == 3
    assert manifest.near_removed == 1
    assert manifest.n_chunks == len(read_chunks(result.output_dir))
    assert [f.path for f in manifest.source_files] == [
        "gadget-guide.md",
        "release-notes.txt",
        "widget-protocol.rst",
    ]
    assert list_dataset_versions(tmp_path) == [result.dataset_version]


def test_dataset_version_depends_on_config_and_inputs(
    fixture_corpus_dir: Path, tmp_path: Path
) -> None:
    a = ingest_directory(fixture_corpus_dir, tmp_path, ChunkingConfig(max_tokens=400))
    b = ingest_directory(fixture_corpus_dir, tmp_path, ChunkingConfig(max_tokens=200))
    c = ingest_directory(fixture_corpus_dir, tmp_path, ChunkingConfig(max_tokens=400))
    assert a.dataset_version != b.dataset_version
    assert a.dataset_version == c.dataset_version
    assert len(list_dataset_versions(tmp_path)) == 2


def test_compute_dataset_version_is_order_independent() -> None:
    files = [
        SourceFile(path="b", sha256="2", size_bytes=1),
        SourceFile(path="a", sha256="1", size_bytes=1),
    ]
    v1 = compute_dataset_version(files, ChunkingConfig(), DedupConfig())
    v2 = compute_dataset_version(list(reversed(files)), ChunkingConfig(), DedupConfig())
    assert v1 == v2
    assert len(v1) == 12


def test_ingest_empty_directory_raises(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        ingest_directory(tmp_path, tmp_path / "out")
