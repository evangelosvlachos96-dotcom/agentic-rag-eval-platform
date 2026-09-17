"""End-to-end runner test on the fixture corpus and fixture eval set with a mocked LLM."""

from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from ragplatform.evals.eval_set import load_eval_set
from ragplatform.evals.results import read_results, read_summary
from ragplatform.evals.runner import EvalRunner, git_state, make_run_id
from ragplatform.ingestion.pipeline import ingest_directory
from ragplatform.llm.cache import CachedProvider
from ragplatform.llm.fake import FakeProvider, mock_responder
from ragplatform.llm.pricing import load_pricing
from ragplatform.pipelines.run_config import RunConfig
from ragplatform.retrieval.config import RetrievalConfig
from ragplatform.retrieval.index import build_index, load_retriever

if TYPE_CHECKING:
    from ragplatform.llm.provider import CompletionRequest

REPO = Path(__file__).resolve().parents[2]
EVAL_SETS_DIR = REPO / "eval_sets"


@pytest.fixture
def dataset_dir(fixture_corpus_dir: Path, tmp_path: Path) -> Path:
    directory = ingest_directory(fixture_corpus_dir, tmp_path / "processed").output_dir
    build_index(directory)  # BM25 only; no embeddings needed for a bm25 config
    return directory


def _runner(
    dataset_dir: Path,
    tmp_path: Path,
    *,
    provider: FakeProvider | None,
    retrieval_only: bool,
    limit: int | None = None,
) -> EvalRunner:
    config = RunConfig(name="bm25_only", retrieval=RetrievalConfig(mode="bm25", final_k=4))
    items, version = load_eval_set(EVAL_SETS_DIR, "fixture")
    if limit:
        items = items[:limit]
    cache = CachedProvider(provider, tmp_path / "llm-cache") if provider else None
    return EvalRunner(
        config=config,
        items=items,
        dataset_dir=dataset_dir,
        retriever=load_retriever(config.retrieval, dataset_dir),
        run_dir=tmp_path / "runs" / make_run_id(config.name),
        eval_set_name="fixture",
        eval_set_version=version,
        provider=cache,
        cache=cache,
        generator_model="fake-model",
        judge_model="fake-model",
        pricing=load_pricing(REPO / "configs" / "pricing.yaml"),
        retrieval_only=retrieval_only,
        repo_dir=REPO,
        bootstrap_resamples=200,
    )


def test_retrieval_only_run_scores_answerable_items(dataset_dir: Path, tmp_path: Path) -> None:
    runner = _runner(dataset_dir, tmp_path, provider=None, retrieval_only=True)
    runner.retrieve_all()
    summary = runner.finalize()
    assert summary.retrieval_only is True
    assert summary.n_items == 5
    assert summary.llm_calls == 0
    assert summary.generator_model is None
    # Unanswerable items are excluded from retrieval metrics: 4 answerable items scored.
    assert summary.metrics["hit@4"].n == 4
    assert summary.metrics["hit@4"].mean == 1.0  # exact terms and headings are easy for BM25
    assert summary.metrics["mrr"].mean > 0.5
    assert set(summary.metrics) == {"hit@1", "hit@4", "recall@4", "precision@4", "mrr", "ndcg@4"}
    assert summary.n_unmatched_labels == 0
    assert "unanswerable" in summary.by_category
    assert summary.by_category["unanswerable"] == {}
    results = read_results(runner.run_dir)
    unanswerable = next(r for r in results if not r.answerable)
    assert unanswerable.metrics == {}
    assert unanswerable.retrieval is not None
    assert len(unanswerable.retrieval.retrieved) == 4
    assert (runner.run_dir / "config.json").exists()
    assert (runner.run_dir / "report.md").read_text(encoding="utf-8").startswith("# Eval run")


async def test_full_run_with_mocked_llm_writes_everything(
    dataset_dir: Path, tmp_path: Path
) -> None:
    provider = FakeProvider(responder=mock_responder)
    runner = _runner(dataset_dir, tmp_path, provider=provider, retrieval_only=False)
    runner.retrieve_all()
    estimate = runner.estimate()
    # 5 items: answer + faithfulness + relevance each, plus correctness for 4 answerable = 19.
    assert estimate.n_llm_calls == 19
    assert estimate.cost_usd == 0.0  # fake-model is priced at zero
    assert estimate.total_usage.input_tokens > 0

    await runner.generate_all()
    summary = runner.finalize()
    assert summary.llm_provider == "cached(fake)"
    assert summary.n_errors == 0
    assert summary.llm_calls == 19
    assert summary.cache_misses == 19
    assert summary.cache_hits == 0
    assert summary.estimated_cost_usd == 0.0
    assert summary.metrics["citations_valid"].mean == 1.0
    assert summary.metrics["correctness"].n == 4
    assert summary.metrics["faithfulness"].n == 5
    assert summary.metrics["missed_abstention"].n == 1
    assert summary.metrics["missed_abstention"].mean == 1.0  # the mock never abstains
    assert summary.prompt_versions["answer"] == "answer_v1"
    assert summary.git_commit is not None

    run_dir = runner.run_dir
    assert sorted(p.name for p in run_dir.iterdir()) == [
        "config.json",
        "report.md",
        "results.jsonl",
        "summary.json",
    ]
    config = json.loads((run_dir / "config.json").read_text(encoding="utf-8"))
    assert config["retrieval"]["mode"] == "bm25"
    results = read_results(run_dir)
    assert len(results) == 5
    first = results[0]
    assert first.answer is not None
    assert first.checks is not None
    assert first.judges is not None
    assert first.judges.correctness is not None
    assert first.answer.citations[0].chunk_id == first.retrieval.retrieved[0].chunk_id  # type: ignore[union-attr]
    assert read_summary(run_dir) == summary
    report = (run_dir / "report.md").read_text(encoding="utf-8")
    assert "Placeholder run" in report
    assert "## Worst" in report
    assert "fixture-0005" in report  # the missed abstention is the worst failure

    # A second run over the same items is served from the disk cache.
    again = _runner(dataset_dir, tmp_path / "second", provider=provider, retrieval_only=False)
    again.cache = CachedProvider(provider, tmp_path / "llm-cache")
    again.provider = again.cache
    again.retrieve_all()
    await again.generate_all()
    second = again.finalize()
    assert second.cache_hits == 19
    assert second.cache_misses == 0
    assert provider.calls == 19


async def test_item_errors_are_recorded_not_raised(dataset_dir: Path, tmp_path: Path) -> None:
    def broken(request: CompletionRequest) -> str:
        if request.purpose.startswith("answer"):
            return "not json"
        return mock_responder(request)

    runner = _runner(
        dataset_dir,
        tmp_path,
        provider=FakeProvider(responder=broken),
        retrieval_only=False,
        limit=2,
    )
    runner.retrieve_all()
    await runner.generate_all()
    summary = runner.finalize()
    assert summary.n_items == 2
    assert summary.n_errors == 2
    results = read_results(runner.run_dir)
    assert all(r.error is not None and "StructuredOutputError" in r.error for r in results)
    assert "**Error:**" in (runner.run_dir / "report.md").read_text(encoding="utf-8")


def test_git_state_and_run_id() -> None:
    commit, dirty = git_state(REPO)
    assert commit is None or len(commit) == 40
    assert dirty is None or isinstance(dirty, bool)
    assert make_run_id("hybrid").endswith("_hybrid")
    assert git_state(Path("/definitely/not/a/repo")) == (None, None)
