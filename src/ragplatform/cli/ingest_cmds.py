"""``rag download-corpus`` and ``rag ingest``.

No ``from __future__ import annotations`` here: typer reads the annotations at
runtime, so the types they mention must be real imports.
"""

from pathlib import Path
from typing import Annotated

import typer

from ragplatform.config import get_settings


def download_corpus(
    dest: Annotated[
        Path | None, typer.Option(help="Target directory (default: <DATA_DIR>/raw/peps).")
    ] = None,
) -> None:
    """Download the pinned PEP corpus and write manifest.json."""
    from ragplatform.ingestion.corpus import DEFAULT_PEPS, PEPS_COMMIT, download_peps

    target = dest or get_settings().raw_corpus_dir
    typer.echo(
        f"Downloading {len(DEFAULT_PEPS)} PEPs at python/peps@{PEPS_COMMIT[:12]} -> {target}"
    )
    manifest = download_peps(target)
    total_bytes = sum(f.size_bytes for f in manifest.files)
    typer.echo(f"Downloaded {len(manifest.files)} files ({total_bytes / 1024:.0f} KiB).")
    if manifest.missing:
        typer.echo(f"Skipped (not present at commit): {manifest.missing}")
    typer.echo(f"Manifest: {target / 'manifest.json'}")


def ingest(
    raw_dir: Annotated[
        Path | None, typer.Option(help="Directory of .rst/.md/.txt files (default: raw corpus).")
    ] = None,
    chunk_size: Annotated[int, typer.Option(min=1, help="Token budget per chunk.")] = 400,
    overlap: Annotated[float, typer.Option(min=0.0, max=0.99, help="Overlap ratio.")] = 0.15,
    no_context_header: Annotated[
        bool, typer.Option("--no-context-header", help="Disable 'title > section' prefix.")
    ] = False,
    dedup_threshold: Annotated[
        float, typer.Option(min=0.0, max=1.0, help="MinHash Jaccard threshold.")
    ] = 0.85,
) -> None:
    """Chunk and deduplicate a corpus into data/processed/<dataset_version>/."""
    from ragplatform.ingestion.chunking import ChunkingConfig
    from ragplatform.ingestion.dedup import DedupConfig
    from ragplatform.ingestion.pipeline import ingest_directory

    settings = get_settings()
    source = raw_dir or settings.raw_corpus_dir
    chunking = ChunkingConfig(
        max_tokens=chunk_size, overlap_ratio=overlap, contextual_header=not no_context_header
    )
    result = ingest_directory(
        source, settings.processed_dir, chunking, DedupConfig(threshold=dedup_threshold)
    )
    m = result.manifest
    typer.echo(f"dataset_version: {result.dataset_version}")
    typer.echo(f"documents: {m.n_documents}  chunks: {m.n_chunks}")
    typer.echo(f"removed: {m.exact_removed} exact, {m.near_removed} near-duplicate")
    typer.echo(f"output: {result.output_dir}")


def register(app: typer.Typer) -> None:
    app.command("download-corpus")(download_corpus)
    app.command("ingest")(ingest)
