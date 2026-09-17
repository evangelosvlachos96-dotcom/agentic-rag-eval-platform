"""The evaluation runner behind ``rag eval run``.

Phases, each callable on its own so the CLI can confirm cost in between:

1. :meth:`EvalRunner.retrieve_all` runs retrieval for every item and computes
   the retrieval metrics (unanswerable items are retrieved but not scored).
2. :meth:`EvalRunner.estimate` prices the generation phase from the real prompts.
3. :meth:`EvalRunner.generate_all` answers, runs programmatic checks, then the
   LLM judges (skipped when the system abstained). Any exception on one item
   is recorded as that item's ``error`` instead of aborting the run.
4. :meth:`EvalRunner.finalize` aggregates with bootstrap CIs and writes the run
   directory (config snapshot, results.jsonl, summary.json, report.md).
"""

from __future__ import annotations

import shutil
import subprocess
from collections import defaultdict
from typing import TYPE_CHECKING

import structlog

from ragplatform.evals.bootstrap import bootstrap_ci
from ragplatform.evals.checks import programmatic_checks
from ragplatform.evals.estimate import CostEstimate, estimate_generation_run
from ragplatform.evals.judges import judge_correctness, judge_faithfulness, judge_relevance
from ragplatform.evals.metrics import hit_at_k, mrr, ndcg_at_k, precision_at_k, recall_at_k
from ragplatform.evals.relevance import count_relevant_chunks, relevance_flags
from ragplatform.evals.report import render_report
from ragplatform.evals.results import (
    CONFIG_FILE,
    REPORT_FILE,
    ItemResult,
    JudgeEvaluation,
    MetricSummary,
    RetrievalEvaluation,
    RetrievedSummary,
    RunSummary,
    write_results,
    write_summary,
)
from ragplatform.generation.generator import generate_answer
from ragplatform.ingestion.chunking import ChunkMetadata
from ragplatform.ingestion.dataset import read_chunks, read_manifest, utc_now_iso
from ragplatform.models import TokenUsage

if TYPE_CHECKING:
    from pathlib import Path

    from ragplatform.evals.models import EvalItem
    from ragplatform.llm.cache import CachedProvider
    from ragplatform.llm.pricing import Pricing
    from ragplatform.llm.provider import LLMProvider
    from ragplatform.models import RetrievedChunk
    from ragplatform.pipelines.run_config import RunConfig
    from ragplatform.retrieval.hybrid import HybridRetriever

log = structlog.get_logger(__name__)


def git_state(repo_dir: Path) -> tuple[str | None, bool | None]:
    """``(commit, dirty)`` for the repository at ``repo_dir``; ``(None, None)`` without git."""
    git = shutil.which("git")
    if git is None:
        return None, None
    try:
        commit = subprocess.run(  # noqa: S603 - fixed argv, no shell
            [git, "rev-parse", "HEAD"], cwd=repo_dir, capture_output=True, text=True, check=True
        ).stdout.strip()
        status = subprocess.run(  # noqa: S603 - fixed argv, no shell
            [git, "status", "--porcelain"],
            cwd=repo_dir,
            capture_output=True,
            text=True,
            check=True,
        ).stdout
    except (subprocess.CalledProcessError, OSError):
        return None, None
    return commit, bool(status.strip())


def make_run_id(config_name: str) -> str:
    stamp = utc_now_iso().replace("-", "").replace(":", "").replace("+0000", "Z")
    return f"{stamp}_{config_name}"


class EvalRunner:
    def __init__(
        self,
        *,
        config: RunConfig,
        items: list[EvalItem],
        dataset_dir: Path,
        retriever: HybridRetriever,
        run_dir: Path,
        eval_set_name: str,
        eval_set_version: str,
        provider: LLMProvider | None = None,
        cache: CachedProvider | None = None,
        generator_model: str | None = None,
        judge_model: str | None = None,
        pricing: Pricing | None = None,
        retrieval_only: bool = False,
        repo_dir: Path | None = None,
        bootstrap_seed: int = 0,
        bootstrap_resamples: int = 1000,
    ) -> None:
        self.config = config
        self.items = items
        self.dataset_dir = dataset_dir
        self.retriever = retriever
        self.run_dir = run_dir
        self.eval_set_name = eval_set_name
        self.eval_set_version = eval_set_version
        self.provider = provider
        self.cache = cache
        self.generator_model = generator_model
        self.judge_model = judge_model
        self.pricing = pricing
        self.retrieval_only = retrieval_only
        self.repo_dir = repo_dir
        self.bootstrap_seed = bootstrap_seed
        self.bootstrap_resamples = bootstrap_resamples
        self.corpus_chunks = read_chunks(dataset_dir)
        self.dataset_version = read_manifest(dataset_dir).dataset_version
        self.retrievals: dict[str, list[RetrievedChunk]] = {}
        self.results: dict[str, ItemResult] = {}
        self.llm_calls = 0
        self.total_usage = TokenUsage(input_tokens=0, output_tokens=0)

    # ------------------------------------------------------------------ retrieval
    def _retrieval_metrics(self, flags: list[bool], n_relevant: int) -> dict[str, float]:
        k = self.config.retrieval.final_k
        return {
            "hit@1": hit_at_k(flags, 1),
            f"hit@{k}": hit_at_k(flags, k),
            f"recall@{k}": recall_at_k(flags, n_relevant, k),
            f"precision@{k}": precision_at_k(flags, k),
            "mrr": mrr(flags),
            f"ndcg@{k}": ndcg_at_k(flags, n_relevant, k),
        }

    def retrieve_all(self) -> None:
        for item in self.items:
            retrieved = self.retriever.retrieve(item.question)
            self.retrievals[item.id] = retrieved
            evaluation: RetrievalEvaluation | None = None
            metrics: dict[str, float] = {}
            flags = relevance_flags(retrieved, item.relevant_sources)
            if item.answerable:
                n_relevant = count_relevant_chunks(self.corpus_chunks, item.relevant_sources)
                metrics = self._retrieval_metrics(flags, n_relevant)
                evaluation = RetrievalEvaluation(
                    retrieved=self._summarize(retrieved, flags),
                    n_relevant_in_corpus=n_relevant,
                    labels_matched=n_relevant > 0,
                    metrics=metrics,
                )
            else:
                evaluation = RetrievalEvaluation(
                    retrieved=self._summarize(retrieved, flags),
                    n_relevant_in_corpus=0,
                    labels_matched=True,
                    metrics={},
                )
            self.results[item.id] = ItemResult(
                item_id=item.id,
                question=item.question,
                category=item.category,
                difficulty=item.difficulty,
                answerable=item.answerable,
                reference_answer=item.reference_answer,
                retrieval=evaluation,
                metrics=metrics,
            )
        log.info("retrieval_phase_complete", items=len(self.items))

    @staticmethod
    def _summarize(retrieved: list[RetrievedChunk], flags: list[bool]) -> list[RetrievedSummary]:
        out: list[RetrievedSummary] = []
        for r, relevant in zip(retrieved, flags, strict=True):
            meta = ChunkMetadata.from_chunk(r.chunk)
            out.append(
                RetrievedSummary(
                    chunk_id=r.chunk.id,
                    doc_id=r.chunk.document_id,
                    doc_title=meta.doc_title,
                    section_path=meta.section_path,
                    rank=r.rank,
                    score=r.score,
                    relevant=relevant,
                )
            )
        return out

    # ------------------------------------------------------------------ generation
    def estimate(self) -> CostEstimate:
        if self.generator_model is None or self.judge_model is None:
            raise ValueError("generator_model and judge_model are required to estimate")
        return estimate_generation_run(
            self.items,
            self.retrievals,
            self.config,
            self.generator_model,
            self.judge_model,
            self.pricing,
        )

    def _account(self, usage: TokenUsage, calls: int = 1) -> None:
        self.llm_calls += calls
        self.total_usage = self.total_usage + usage

    async def _judge(
        self, item: EvalItem, answer_text: str, context: list[RetrievedChunk]
    ) -> tuple[JudgeEvaluation, dict[str, float]]:
        if self.provider is None or self.judge_model is None:
            raise ValueError("judging needs a provider and a judge model")
        metrics: dict[str, float] = {}
        usage = TokenUsage(input_tokens=0, output_tokens=0)
        faith, r = await judge_faithfulness(
            self.provider, self.config.judge, self.judge_model, item.question, answer_text, context
        )
        usage = usage + r.usage
        self._account(r.usage, 2 if r.repaired else 1)
        if faith.score is not None:
            metrics["faithfulness"] = faith.score
        rel, r = await judge_relevance(
            self.provider, self.config.judge, self.judge_model, item.question, answer_text
        )
        usage = usage + r.usage
        self._account(r.usage, 2 if r.repaired else 1)
        metrics["relevance"] = 1.0 if rel.relevant else 0.0
        correctness = None
        if item.answerable:
            correctness, r = await judge_correctness(
                self.provider,
                self.config.judge,
                self.judge_model,
                item.question,
                answer_text,
                item.reference_answer,
            )
            usage = usage + r.usage
            self._account(r.usage, 2 if r.repaired else 1)
            metrics["correctness"] = 1.0 if correctness.correct else 0.0
        return JudgeEvaluation(
            faithfulness=faith, correctness=correctness, relevance=rel, usage=usage
        ), metrics

    async def _generate_item(self, item: EvalItem) -> ItemResult:
        if self.provider is None or self.generator_model is None:
            raise ValueError("generation needs a provider and a generator model")
        base = self.results[item.id]
        context = self.retrievals[item.id]
        answer = await generate_answer(
            item.question, context, self.provider, self.config.generation, self.generator_model
        )
        if answer.usage is not None:
            self._account(answer.usage, 2 if answer.metadata.get("repaired") else 1)
        checks = programmatic_checks(answer, item)
        metrics = dict(base.metrics)
        metrics["abstained"] = 1.0 if checks.abstained else 0.0
        if item.answerable:
            metrics["unnecessary_abstention"] = 1.0 if checks.unnecessary_abstention else 0.0
        else:
            metrics["correct_abstention"] = 1.0 if checks.correct_abstention else 0.0
            metrics["missed_abstention"] = 1.0 if checks.missed_abstention else 0.0
        judges: JudgeEvaluation | None = None
        if not checks.abstained:
            metrics["citations_valid"] = 1.0 if checks.citations_valid else 0.0
            metrics["answered_without_citations"] = (
                1.0 if checks.answered_without_citations else 0.0
            )
            judges, judge_metrics = await self._judge(item, answer.text, context)
            metrics.update(judge_metrics)
        elif item.answerable:
            metrics["correctness"] = 0.0  # abstaining on an answerable item is not a correct answer
        return base.model_copy(
            update={"answer": answer, "checks": checks, "judges": judges, "metrics": metrics}
        )

    async def generate_all(self) -> None:
        if self.provider is None:
            raise ValueError("a provider is required for the generation phase")
        for item in self.items:
            try:
                self.results[item.id] = await self._generate_item(item)
            except Exception as exc:  # one bad item must not kill the run
                log.warning("item_failed", item_id=item.id, error=str(exc))
                self.results[item.id] = self.results[item.id].model_copy(
                    update={"error": f"{type(exc).__name__}: {exc}"}
                )
        log.info("generation_phase_complete", items=len(self.items), llm_calls=self.llm_calls)

    # ------------------------------------------------------------------ aggregation
    def _aggregate(self, results: list[ItemResult]) -> dict[str, MetricSummary]:
        values: dict[str, list[float]] = defaultdict(list)
        for result in results:
            for name, value in result.metrics.items():
                values[name].append(value)
        summary: dict[str, MetricSummary] = {}
        for name, sample in values.items():
            ci = bootstrap_ci(sample, self.bootstrap_resamples, self.bootstrap_seed)
            summary[name] = MetricSummary(
                mean=ci.mean, ci_lower=ci.lower, ci_upper=ci.upper, n=ci.n
            )
        return summary

    def finalize(self) -> RunSummary:
        results = [self.results[item.id] for item in self.items]
        by_category: dict[str, dict[str, MetricSummary]] = {}
        for category in sorted({r.category for r in results}):
            by_category[category] = self._aggregate([r for r in results if r.category == category])
        commit, dirty = git_state(self.repo_dir) if self.repo_dir is not None else (None, None)
        cost: float | None = None
        if self.pricing is not None and not self.retrieval_only and self.generator_model:
            try:
                cost = self.pricing.cost_usd(self.generator_model, self.total_usage)
            except KeyError:
                cost = None
        summary = RunSummary(
            run_id=self.run_dir.name,
            config_name=self.config.name,
            created_at=utc_now_iso(),
            git_commit=commit,
            git_dirty=dirty,
            dataset_version=self.dataset_version,
            eval_set_name=self.eval_set_name,
            eval_set_version=self.eval_set_version,
            prompt_versions={
                "answer": self.config.generation.prompt_version,
                "judge_faithfulness": self.config.judge.faithfulness_prompt,
                "judge_correctness": self.config.judge.correctness_prompt,
                "judge_relevance": self.config.judge.relevance_prompt,
            },
            generator_model=None if self.retrieval_only else self.generator_model,
            judge_model=None if self.retrieval_only else self.judge_model,
            llm_provider=None if self.provider is None else self.provider.name,
            retrieval_only=self.retrieval_only,
            n_items=len(results),
            n_errors=sum(1 for r in results if r.error),
            n_unmatched_labels=sum(
                1 for r in results if r.retrieval is not None and not r.retrieval.labels_matched
            ),
            metrics=self._aggregate(results),
            by_category=by_category,
            llm_calls=self.llm_calls,
            cache_hits=self.cache.hits if self.cache else 0,
            cache_misses=self.cache.misses if self.cache else 0,
            total_usage=self.total_usage,
            estimated_cost_usd=cost,
            bootstrap_seed=self.bootstrap_seed,
            bootstrap_resamples=self.bootstrap_resamples,
        )
        self.run_dir.mkdir(parents=True, exist_ok=True)
        (self.run_dir / CONFIG_FILE).write_text(
            self.config.model_dump_json(indent=2), encoding="utf-8"
        )
        write_results(self.run_dir, results)
        write_summary(self.run_dir, summary)
        (self.run_dir / REPORT_FILE).write_text(render_report(summary, results), encoding="utf-8")
        log.info("run_written", run_dir=self.run_dir.as_posix())
        return summary
