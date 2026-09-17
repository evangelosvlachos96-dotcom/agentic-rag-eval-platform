"""``rag eval generate-candidates | review | run | compare``.

No ``from __future__ import annotations`` here: typer reads the annotations at
runtime, so the types they mention must be real imports.
"""

import asyncio
from pathlib import Path
from typing import Annotated, cast

import typer

from ragplatform.cli.retrieval_cmds import resolve_dataset_dir
from ragplatform.config import Settings, get_settings
from ragplatform.evals.candidates import Candidate
from ragplatform.evals.models import ANSWERABLE_CATEGORIES, CATEGORIES, Category, SourceRef
from ragplatform.evals.review import ReviewSession
from ragplatform.llm.provider import LLMProvider

eval_app = typer.Typer(
    help="Evaluation: candidates, review, runs and comparisons.", no_args_is_help=True
)

PLACEHOLDER_NOTE = (
    "NOTE: --mock-llm uses canned placeholder responses. Use it only to check the pipeline; "
    "never report its numbers."
)


def _provider(settings: Settings, mock_llm: bool) -> LLMProvider:
    if mock_llm:
        from ragplatform.llm.fake import FakeProvider, mock_responder

        typer.echo(PLACEHOLDER_NOTE)
        return FakeProvider(responder=mock_responder)
    if not settings.has_anthropic_key:
        raise typer.BadParameter(
            "ANTHROPIC_API_KEY is not set (or pass --mock-llm for a smoke run)"
        )
    from ragplatform.llm.anthropic_provider import AnthropicProvider

    return AnthropicProvider.from_settings(settings)


@eval_app.command("generate-candidates")
def generate_candidates(
    n: Annotated[int, typer.Option(min=1, help="Number of candidates to write.")] = 120,
    dataset_version: Annotated[str | None, typer.Option()] = None,
    taxonomy: Annotated[Path, typer.Option()] = Path("eval_sets/taxonomy_v1.yaml"),
    unanswerable_ratio: Annotated[float, typer.Option(min=0.0, max=1.0)] = 0.15,
    seed: Annotated[int, typer.Option()] = 0,
    model: Annotated[str | None, typer.Option(help="Defaults to ANTHROPIC_MODEL.")] = None,
    mock_llm: Annotated[bool, typer.Option("--mock-llm", hidden=True)] = False,
) -> None:
    """Sample chunks and ask the LLM for candidate questions (to be reviewed by a human)."""
    from ragplatform.evals.candidates import generate_candidates as _generate
    from ragplatform.evals.candidates import write_candidates
    from ragplatform.evals.taxonomy import load_taxonomy
    from ragplatform.ingestion.dataset import read_chunks, utc_now_iso
    from ragplatform.llm.cache import CachedProvider

    settings = get_settings()
    chunks = read_chunks(resolve_dataset_dir(dataset_version))
    provider = CachedProvider(_provider(settings, mock_llm), settings.llm_cache_dir)
    chosen_model = model or settings.anthropic_model
    stamp = utc_now_iso().replace(":", "").replace("-", "").replace("+0000", "Z")
    candidates = asyncio.run(
        _generate(
            chunks,
            n,
            provider,
            chosen_model,
            load_taxonomy(taxonomy),
            unanswerable_ratio=unanswerable_ratio,
            seed=seed,
            batch_id=stamp,
        )
    )
    out = settings.eval_sets_dir / "candidates" / f"{stamp}.jsonl"
    write_candidates(out, candidates)
    typer.echo(f"wrote {len(candidates)} candidates to {out}")
    typer.echo(f"LLM cache: {provider.hits} hits, {provider.misses} misses")
    typer.echo(f"next: rag eval review {out}")


def _show_candidate(candidate: Candidate, session: ReviewSession) -> None:
    progress = session.progress()
    done = progress.accepted + progress.rejected
    typer.echo("")
    typer.echo("=" * 78)
    typer.echo(
        f"[{done + 1}/{progress.total}] accepted={progress.accepted} rejected={progress.rejected} "
        f"| items in set: {progress.items_in_set} "
        f"({progress.unanswerable_share:.0%} unanswerable) {progress.category_counts}"
    )
    typer.echo("=" * 78)
    typer.echo(f"id:         {candidate.id}")
    typer.echo(f"category:   {candidate.category} (target {candidate.target_category})")
    typer.echo(f"difficulty: {candidate.difficulty}   answerable: {candidate.answerable}")
    typer.echo(f"question:   {candidate.question}")
    typer.echo(f"reference:  {candidate.reference_answer}")
    typer.echo(
        f"source:     {candidate.source.doc_title} > {candidate.source.section_path} "
        f"(doc {candidate.source.doc_id}, chunk {candidate.source.chunk_id})"
    )
    typer.echo("-" * 78)
    typer.echo(candidate.source.text)
    typer.echo("-" * 78)


def _edit_sources(candidate: Candidate) -> list[SourceRef]:
    doc_id = typer.prompt("doc_id", default=candidate.source.doc_id)
    raw = typer.prompt(
        "section path(s), ';'-separated ('' = whole document)",
        default=candidate.source.section_path,
    )
    return [SourceRef(doc_id=doc_id, section_path=p.strip()) for p in raw.split(";")]


def _prompt_category(default: str) -> Category:
    while True:
        value = typer.prompt(f"category {list(CATEGORIES)}", default=default)
        if value in CATEGORIES:
            return cast("Category", value)
        typer.echo("unknown category")


@eval_app.command("review")
def review(
    candidates_file: Annotated[Path, typer.Argument(help="eval_sets/candidates/<ts>.jsonl")],
    eval_set: Annotated[str, typer.Option(help="Target eval set name under eval_sets/.")] = "v1",
) -> None:
    """Accept, edit or reject candidates; accepted items go to eval_sets/<set>/items.jsonl."""
    settings = get_settings()
    session = ReviewSession(candidates_file, settings.eval_sets_dir / eval_set, eval_set)
    typer.echo("commands: [a]ccept  [e]dit then accept  [r]eject  [q]uit (resume later)")
    for candidate in session.pending():
        _show_candidate(candidate, session)
        while True:
            choice = typer.prompt("a / e / r / q", default="a").strip().lower()
            if choice in {"a", "e", "r", "q"}:
                break
        if choice == "q":
            break
        if choice == "r":
            session.reject(candidate)
            continue
        if choice == "a":
            session.accept(candidate)
            continue
        question = typer.prompt("question", default=candidate.question)
        reference = typer.prompt("reference answer", default=candidate.reference_answer)
        category = _prompt_category(candidate.category)
        sources = _edit_sources(candidate) if category in ANSWERABLE_CATEGORIES else []
        notes = typer.prompt("notes", default="")
        session.accept(
            candidate,
            question=question,
            reference_answer=reference,
            category=category,
            sources=sources,
            notes=notes,
        )
    progress = session.progress()
    typer.echo("")
    typer.echo(
        f"done: accepted={progress.accepted} rejected={progress.rejected} "
        f"pending={progress.pending} | items in {eval_set}: {progress.items_in_set} "
        f"({progress.unanswerable_share:.0%} unanswerable) {progress.category_counts}"
    )


@eval_app.command("run")
def run(
    config: Annotated[Path, typer.Option(help="Run config YAML.")] = Path("configs/hybrid.yaml"),
    eval_set: Annotated[str, typer.Option(help="Eval set name under eval_sets/.")] = "v1",
    limit: Annotated[int | None, typer.Option(min=1, help="Only the first N items.")] = None,
    retrieval_only: Annotated[bool, typer.Option("--retrieval-only")] = False,
    yes: Annotated[bool, typer.Option("--yes", "-y", help="Skip the cost confirmation.")] = False,
    dataset_version: Annotated[str | None, typer.Option()] = None,
    mock_llm: Annotated[
        bool, typer.Option("--mock-llm", help="Smoke-test with canned placeholder responses.")
    ] = False,
    seed: Annotated[int, typer.Option(help="Bootstrap seed.")] = 0,
) -> None:
    """Evaluate a config on an eval set and write experiments/runs/<timestamp>_<config>/."""
    from ragplatform.evals.eval_set import load_eval_set
    from ragplatform.evals.runner import EvalRunner, make_run_id
    from ragplatform.llm.cache import CachedProvider
    from ragplatform.llm.pricing import load_pricing
    from ragplatform.pipelines.run_config import load_run_config
    from ragplatform.retrieval.index import load_retriever

    settings = get_settings()
    run_config = load_run_config(config)
    items, version = load_eval_set(settings.eval_sets_dir, eval_set)
    if limit is not None:
        items = items[:limit]
    dataset_dir = resolve_dataset_dir(dataset_version)
    retriever = load_retriever(run_config.retrieval, dataset_dir)
    pricing_path = settings.configs_dir / "pricing.yaml"
    pricing = load_pricing(pricing_path) if pricing_path.exists() else None

    provider: LLMProvider | None = None
    cache: CachedProvider | None = None
    generator_model = run_config.generation.model or settings.anthropic_model
    judge_model = run_config.judge.model or settings.anthropic_judge_model
    if not retrieval_only:
        cache = CachedProvider(_provider(settings, mock_llm), settings.llm_cache_dir)
        provider = cache
        if mock_llm:
            generator_model = judge_model = "fake-model"

    run_dir = settings.experiments_dir / "runs" / make_run_id(run_config.name)
    runner = EvalRunner(
        config=run_config,
        items=items,
        dataset_dir=dataset_dir,
        retriever=retriever,
        run_dir=run_dir,
        eval_set_name=eval_set,
        eval_set_version=version,
        provider=provider,
        cache=cache,
        generator_model=generator_model,
        judge_model=judge_model,
        pricing=pricing,
        retrieval_only=retrieval_only,
        repo_dir=Path.cwd(),
        bootstrap_seed=seed,
    )
    typer.echo(
        f"eval set {eval_set}@{version}: {len(items)} items; dataset {runner.dataset_version}"
    )
    runner.retrieve_all()
    if not retrieval_only:
        estimate = runner.estimate()
        cost = (
            f"${estimate.cost_usd:.2f}" if estimate.cost_usd is not None else "unknown (no price)"
        )
        typer.echo(
            f"generation phase: ~{estimate.n_llm_calls} LLM calls, "
            f"~{estimate.total_usage.input_tokens} input / ~{estimate.total_usage.output_tokens} "
            f"output tokens, estimated cost {cost} "
            f"(generator {estimate.generator_model}, judge {estimate.judge_model}); "
            "cached calls are free"
        )
        if not yes and not typer.confirm("proceed?", default=False):
            raise typer.Abort()
        asyncio.run(runner.generate_all())
    summary = runner.finalize()
    typer.echo(f"run written to {run_dir}")
    for name, metric in sorted(summary.metrics.items()):
        ci = f"[{metric.ci_lower:.3f}, {metric.ci_upper:.3f}]"
        typer.echo(f"  {name:<28} {metric.mean:.3f}  {ci}  n={metric.n}")
    if summary.n_errors:
        typer.echo(f"  errors: {summary.n_errors} (see results.jsonl)")
    if cache is not None:
        typer.echo(
            f"  LLM calls: {summary.llm_calls}, cache hits {cache.hits}, misses {cache.misses}"
        )


@eval_app.command("compare")
def compare(
    run_a: Annotated[Path, typer.Argument(help="Baseline run directory.")],
    run_b: Annotated[Path, typer.Argument(help="Candidate run directory.")],
    seed: Annotated[int, typer.Option()] = 0,
) -> None:
    """Per-metric deltas between two runs with paired bootstrap 95% CIs."""
    from ragplatform.evals.compare import compare_runs, render_comparison

    typer.echo(render_comparison(compare_runs(run_a, run_b, seed=seed)))
