"""``rag index`` and ``rag query``.

No ``from __future__ import annotations`` here: typer reads the annotations at
runtime, so the types they mention must be real imports.
"""

import asyncio
from pathlib import Path
from typing import Annotated

import typer

from ragplatform.config import get_settings
from ragplatform.models import RetrievedChunk


def resolve_dataset_dir(dataset_version: str | None) -> Path:
    """The processed dataset directory for a version, or the newest one when None."""
    from ragplatform.ingestion.dataset import dataset_dir, list_dataset_versions

    settings = get_settings()
    if dataset_version is None:
        versions = list_dataset_versions(settings.processed_dir)
        if not versions:
            raise typer.BadParameter("no processed dataset found; run `rag ingest` first")
        dataset_version = versions[0]
    directory = dataset_dir(settings.processed_dir, dataset_version)
    if not directory.exists():
        raise typer.BadParameter(f"dataset version {dataset_version!r} not found in {directory}")
    return directory


def index(
    dataset_version: Annotated[
        str | None, typer.Option(help="Dataset version to index (default: newest).")
    ] = None,
    config: Annotated[Path, typer.Option(help="Run config whose embedding model to use.")] = Path(
        "configs/hybrid_rerank.yaml"
    ),
    no_vectors: Annotated[
        bool, typer.Option("--no-vectors", help="Build only the BM25 index (no model download).")
    ] = False,
    force: Annotated[bool, typer.Option(help="Recompute embeddings even if cached.")] = False,
) -> None:
    """Build the BM25 index and the embedding vector store for a dataset version."""
    from ragplatform.pipelines.run_config import load_run_config
    from ragplatform.retrieval.index import build_index, make_embedder

    directory = resolve_dataset_dir(dataset_version)
    embedder = None if no_vectors else make_embedder(load_run_config(config).retrieval)
    report = build_index(directory, embedder, force=force)
    typer.echo(f"dataset_version: {report.dataset_version}  chunks: {report.n_chunks}")
    typer.echo(f"bm25: {report.bm25_path}")
    if report.vectors_path is not None:
        state = "reused cached embeddings" if report.embeddings_reused else "embedded"
        typer.echo(f"vectors: {report.vectors_path} ({state})")


def _format_stages(result: RetrievedChunk) -> str:
    return "  ".join(
        f"{stage}=#{score.rank}({score.score:.3f})" for stage, score in result.stages.items()
    )


def query(
    question: Annotated[str, typer.Argument(help="The question to answer.")],
    config: Annotated[Path, typer.Option(help="Run config YAML.")] = Path(
        "configs/hybrid_rerank.yaml"
    ),
    dataset_version: Annotated[str | None, typer.Option()] = None,
    show_chunks: Annotated[
        bool, typer.Option("--show-chunks", help="Print retrieved chunks and stage scores.")
    ] = False,
    no_generate: Annotated[
        bool, typer.Option("--no-generate", help="Retrieve only; never call the LLM.")
    ] = False,
) -> None:
    """Retrieve chunks for a question and generate a grounded answer."""
    from ragplatform.ingestion.chunking import ChunkMetadata
    from ragplatform.pipelines.run_config import load_run_config
    from ragplatform.retrieval.index import load_retriever

    settings = get_settings()
    run_config = load_run_config(config)
    retriever = load_retriever(run_config.retrieval, resolve_dataset_dir(dataset_version))
    results = retriever.retrieve(question)

    typer.echo(f"config: {run_config.name}  retriever: {run_config.retrieval.retriever_name}")
    typer.echo(f"retrieved {len(results)} chunks")
    for result in results:
        meta = ChunkMetadata.from_chunk(result.chunk)
        header = f"{meta.doc_title} > {meta.section_path}" if meta.section_path else meta.doc_title
        typer.echo(f"  [{result.rank}] {result.chunk.id}  {header}")
        if show_chunks:
            typer.echo(f"      stages: {_format_stages(result)}")
            preview = result.chunk.content.replace("\n", " ")
            typer.echo(f"      {preview[:300]}{'...' if len(preview) > 300 else ''}")

    if no_generate:
        return
    if not settings.has_anthropic_key:
        typer.echo("generation skipped: ANTHROPIC_API_KEY is not set")
        return

    from ragplatform.generation import generate_answer
    from ragplatform.llm.anthropic_provider import AnthropicProvider

    provider = AnthropicProvider.from_settings(settings)
    model = run_config.generation.model or settings.anthropic_model
    answer = asyncio.run(generate_answer(question, results, provider, run_config.generation, model))
    typer.echo("")
    if answer.abstained:
        typer.echo("ABSTAINED: the retrieved context does not answer the question.")
    if answer.text:
        typer.echo(answer.text)
    typer.echo(f"citations: {[c.chunk_id for c in answer.citations]}")
    if answer.invalid_citations:
        typer.echo(f"invalid citations removed: {answer.invalid_citations}")
    typer.echo(f"model: {answer.model}  prompt: {answer.prompt_version}  usage: {answer.usage}")


def register(app: typer.Typer) -> None:
    app.command("index")(index)
    app.command("query")(query)
