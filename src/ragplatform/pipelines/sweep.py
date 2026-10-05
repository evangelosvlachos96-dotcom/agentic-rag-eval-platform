"""Reproducible BM25 chunking experiments, with no provider or vector-model calls."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import BaseModel, ConfigDict, Field

from ragplatform.evals.readiness import audit_eval_set
from ragplatform.evals.runner import EvalRunner
from ragplatform.ingestion.chunking import ChunkingConfig
from ragplatform.ingestion.dataset import read_chunks
from ragplatform.ingestion.pipeline import ingest_directory
from ragplatform.pipelines.run_config import RunConfig
from ragplatform.retrieval.config import RetrievalConfig
from ragplatform.retrieval.index import build_index, load_retriever

if TYPE_CHECKING:
    from pathlib import Path

    from ragplatform.evals.models import EvalItem
    from ragplatform.evals.results import RunSummary


class ChunkingVariant(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    name: str = Field(pattern=r"^[a-z][a-z0-9_]*$")
    chunking: ChunkingConfig


def run_variant(
    variant: ChunkingVariant,
    *,
    raw_dir: Path,
    processed_root: Path,
    run_dir: Path,
    items: list[EvalItem],
    eval_version: str,
    repo_dir: Path,
    eval_name: str = "v1",
) -> RunSummary:
    """Refuse overwrite, audit labels, and save a complete retrieval-only run."""
    if run_dir.exists():
        raise FileExistsError(f"Run already exists: {run_dir.name}")
    ingested = ingest_directory(raw_dir, processed_root, chunking=variant.chunking)
    audit = audit_eval_set(items, read_chunks(ingested.output_dir))
    if not audit.ready:
        raise ValueError("Label audit failed: " + "; ".join(audit.errors))
    build_index(ingested.output_dir, embedder=None)
    config = RunConfig(
        name=variant.name, retrieval=RetrievalConfig(mode="bm25", rerank=False, final_k=8)
    )
    runner = EvalRunner(
        config=config,
        items=items,
        dataset_dir=ingested.output_dir,
        retriever=load_retriever(config.retrieval, ingested.output_dir),
        run_dir=run_dir,
        eval_set_name=eval_name,
        eval_set_version=eval_version,
        retrieval_only=True,
        repo_dir=repo_dir,
    )
    runner.retrieve_all()
    summary = runner.finalize()
    # Portable provenance: source files keep their hashes; host path is not needed.
    source_name = (
        raw_dir.relative_to(repo_dir).as_posix()
        if raw_dir.is_relative_to(repo_dir)
        else raw_dir.name
    )
    manifest = ingested.manifest.model_copy(update={"source_dir": source_name})
    (run_dir / "dataset-manifest.json").write_text(
        manifest.model_dump_json(indent=2), encoding="utf-8"
    )
    (run_dir / "label-audit.json").write_text(audit.model_dump_json(indent=2), encoding="utf-8")
    return summary
