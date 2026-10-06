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
    dry_run: Annotated[bool, typer.Option(help="Preview calls without contacting an LLM.")] = False,
    yes: Annotated[bool, typer.Option("--yes", help="Approve paid candidate generation.")] = False,
) -> None:
    """Sample chunks and ask the LLM for candidate questions (to be reviewed by a human)."""
    from ragplatform.evals.candidates import generate_candidates as _generate
    from ragplatform.evals.candidates import write_candidates
    from ragplatform.evals.taxonomy import load_taxonomy
    from ragplatform.ingestion.dataset import read_chunks, utc_now_iso
    from ragplatform.llm.cache import CachedProvider

    settings = get_settings()
    chunks = read_chunks(resolve_dataset_dir(dataset_version))
    chosen_model = model or settings.anthropic_model
    from ragplatform.evals.candidates import stratified_sample

    count = len(stratified_sample(chunks, n, seed))
    from ragplatform.evals.candidate_plan import candidate_usage
    from ragplatform.llm.pricing import load_pricing

    tax = load_taxonomy(taxonomy)
    usage = candidate_usage(chunks, n, tax, unanswerable_ratio, seed)
    price_path = settings.configs_dir / "pricing.yaml"
    cost = "unknown (no matching configured price)"
    if price_path.exists():
        pricing = load_pricing(price_path)
        try:
            cost = (
                f"${pricing.cost_usd(chosen_model, usage):.4f} (prices dated {pricing.checked_on})"
            )
        except KeyError:
            cost = "unknown (no matching configured price)"
    typer.echo(
        f"Candidate plan: {count} initial LLM calls; up to {count} repair calls; "
        f"model {chosen_model}; max 4096 output tokens per call."
    )
    typer.echo("Actual cost depends on token usage and model pricing; this is not a spending cap.")
    typer.echo(f"Planning allowance including one repair per candidate: {cost}")
    if dry_run:
        typer.echo("Dry run: zero LLM calls. No candidates written.")
        return
    if (
        not mock_llm
        and not yes
        and not typer.confirm("Allow paid candidate generation?", default=False)
    ):
        raise typer.Abort()
    provider = CachedProvider(_provider(settings, mock_llm), settings.llm_cache_dir)
    stamp = utc_now_iso().replace(":", "").replace("-", "").replace("+0000", "Z")
    candidates = asyncio.run(
        _generate(
            chunks,
            n,
            provider,
            chosen_model,
            tax,
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
    for source in candidate.additional_sources:
        typer.echo(
            f"Additional source: {source.doc_title} > {source.section_path} ({source.doc_id})"
        )
        typer.echo(source.text)
    typer.echo("-" * 78)


def _edit_sources(candidate: Candidate) -> list[SourceRef]:
    defaults = list(
        dict.fromkeys(
            (source.doc_id, source.section_path)
            for source in [candidate.source, *candidate.additional_sources]
        )
    )
    sources: list[SourceRef] = []
    for doc, section in defaults:
        if typer.confirm(f"Keep or edit source {doc} > {section}?", default=True):
            doc_id = typer.prompt("doc_id", default=doc)
            path = typer.prompt("section path (empty = whole document)", default=section)
            sources.append(SourceRef(doc_id=doc_id, section_path=path.strip()))
    while not sources or typer.confirm("Add another source?", default=False):
        doc_id = typer.prompt("doc_id")
        path = typer.prompt("section path (empty = whole document)", default="")
        sources.append(SourceRef(doc_id=doc_id, section_path=path.strip()))
    return list(dict.fromkeys(sources))


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
    dry_run: Annotated[
        bool, typer.Option(help="Plan generation without constructing a provider.")
    ] = False,
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
        typer.echo(
            "Planning allowance, not a spending cap; repair calls and SDK retries may add cost."
        )
        if pricing is not None:
            typer.echo(
                f"Pricing snapshot last checked: {pricing.checked_on}; verify before paid use."
            )
        if dry_run:
            typer.echo("Dry run complete: zero LLM calls; no provider constructed.")
            return
        if not yes and not typer.confirm("proceed?", default=False):
            raise typer.Abort()
        cache = CachedProvider(_provider(settings, mock_llm), settings.llm_cache_dir)
        runner.cache = cache
        runner.provider = cache
        asyncio.run(runner.generate_all())
    if dry_run:
        typer.echo("Dry run complete: zero LLM calls; no provider constructed.")
        return
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


@eval_app.command("audit")
def audit(
    eval_set: Annotated[str, typer.Option()] = "v1",
    dataset_version: Annotated[str | None, typer.Option()] = None,
) -> None:
    """Check reviewed labels and coverage offline; no LLM calls."""
    from ragplatform.evals.eval_set import load_eval_set
    from ragplatform.evals.readiness import audit_eval_set
    from ragplatform.ingestion.dataset import read_chunks

    items, version = load_eval_set(get_settings().eval_sets_dir, eval_set)
    report = audit_eval_set(items, read_chunks(resolve_dataset_dir(dataset_version)))
    typer.echo(f"Eval set {eval_set}@{version}; offline checks only, not human validation.")
    typer.echo(report.model_dump_json(indent=2))
    if not report.ready:
        raise typer.Exit(code=1)


@eval_app.command("baseline")
def baseline(
    eval_set: Annotated[str, typer.Option()] = "v1",
    dataset_version: Annotated[str | None, typer.Option()] = None,
    config: Annotated[
        list[Path] | None, typer.Option(help="Repeat for each retrieval config.")
    ] = None,
    seed: Annotated[int, typer.Option()] = 0,
) -> None:
    """Audit a reviewed set, then run retrieval-only baselines. Never creates an LLM provider."""
    from ragplatform.pipelines.run_config import load_run_config
    from ragplatform.retrieval.index import load_retriever

    audit(eval_set=eval_set, dataset_version=dataset_version)
    paths = config or [get_settings().configs_dir / "bm25_only.yaml"]
    directory = resolve_dataset_dir(dataset_version)
    # Check every index/model before writing any runs, avoiding partial suites on setup errors.
    for path in paths:
        load_retriever(load_run_config(path).retrieval, directory)
    typer.echo("Retrieval-only baseline: zero Anthropic calls; generation quality is not measured.")
    for path in paths:
        run(
            config=path,
            eval_set=eval_set,
            limit=None,
            retrieval_only=True,
            yes=False,
            dataset_version=dataset_version,
            mock_llm=False,
            seed=seed,
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
