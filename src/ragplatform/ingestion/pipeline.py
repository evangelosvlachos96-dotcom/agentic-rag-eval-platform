"""The ingest pipeline: raw files -> loaded documents -> chunks -> dedup -> dataset on disk."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import structlog
from pydantic import BaseModel, ConfigDict

from ragplatform.ingestion.chunking import ChunkingConfig, chunk_document
from ragplatform.ingestion.dataset import (
    DatasetManifest,
    DocumentSummary,
    SourceFile,
    compute_dataset_version,
    dataset_dir,
    sha256_file,
    utc_now_iso,
    write_dataset,
)
from ragplatform.ingestion.dedup import DedupConfig, DedupReport, dedup_chunks
from ragplatform.ingestion.loaders import SUPPORTED_SUFFIXES, load_file

if TYPE_CHECKING:
    from ragplatform.ingestion.tokens import TokenCounter
    from ragplatform.models import Chunk

log = structlog.get_logger(__name__)


class IngestResult(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    dataset_version: str
    output_dir: Path
    manifest: DatasetManifest
    dedup: DedupReport


def discover_files(raw_dir: Path) -> list[Path]:
    """Supported files under ``raw_dir``, sorted for determinism."""
    return sorted(
        p for p in raw_dir.rglob("*") if p.is_file() and p.suffix.lower() in SUPPORTED_SUFFIXES
    )


def ingest_directory(
    raw_dir: Path,
    processed_root: Path,
    chunking: ChunkingConfig | None = None,
    dedup: DedupConfig | None = None,
    counter: TokenCounter | None = None,
) -> IngestResult:
    """Load, chunk and deduplicate every supported file, then write the dataset."""
    chunking = chunking or ChunkingConfig()
    dedup = dedup or DedupConfig()
    files = discover_files(raw_dir)
    if not files:
        raise FileNotFoundError(f"no {sorted(SUPPORTED_SUFFIXES)} files under {raw_dir}")

    source_files = [
        SourceFile(
            path=path.relative_to(raw_dir).as_posix(),
            sha256=sha256_file(path),
            size_bytes=path.stat().st_size,
        )
        for path in files
    ]
    version = compute_dataset_version(source_files, chunking, dedup)
    output_dir = dataset_dir(processed_root, version)

    all_chunks: list[Chunk] = []
    summaries: list[DocumentSummary] = []
    for path in files:
        parsed = load_file(path, source=path.relative_to(raw_dir).as_posix())
        chunks = chunk_document(parsed, chunking, counter)
        all_chunks.extend(chunks)
        summaries.append(
            DocumentSummary(
                doc_id=parsed.document.id,
                title=parsed.title,
                source=parsed.document.source,
                n_chunks=len(chunks),
            )
        )
        log.debug("document_chunked", source=parsed.document.source, chunks=len(chunks))

    kept, report = dedup_chunks(all_chunks, dedup)
    manifest = DatasetManifest(
        dataset_version=version,
        created_at=utc_now_iso(),
        source_dir=raw_dir.as_posix(),
        source_files=source_files,
        chunking=chunking,
        dedup=dedup,
        n_documents=len(summaries),
        n_chunks=len(kept),
        exact_removed=report.exact_removed,
        near_removed=report.near_removed,
        documents=summaries,
    )
    write_dataset(output_dir, kept, manifest)
    log.info(
        "ingest_complete",
        dataset_version=version,
        documents=len(summaries),
        chunks=len(kept),
        output_dir=output_dir.as_posix(),
    )
    return IngestResult(
        dataset_version=version, output_dir=output_dir, manifest=manifest, dedup=report
    )
