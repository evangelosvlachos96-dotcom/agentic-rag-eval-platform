"""Owner-approved paid validation. Requires a local key and an explicit --execute flag."""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import shutil
from pathlib import Path

from ragplatform.agent.loop import run_agent
from ragplatform.agent.models import AgentConfig
from ragplatform.config import get_settings
from ragplatform.evals.eval_set import load_eval_set
from ragplatform.evals.runner import EvalRunner, make_run_id
from ragplatform.llm.anthropic_provider import AnthropicProvider
from ragplatform.llm.budget import BudgetedProvider
from ragplatform.llm.cache import CachedProvider
from ragplatform.llm.pricing import load_pricing
from ragplatform.pipelines.run_config import GenerationConfig, JudgeConfig, load_run_config
from ragplatform.retrieval.index import load_retriever

ROOT = Path(__file__).resolve().parents[1]
SESSION = ROOT / "experiments/live-validation"
EVIDENCE = ROOT / "docs/evidence/live-validation"
DATASET = ROOT / "data/processed/27b46e65f45d"
GENERATOR = "claude-sonnet-5"
JUDGE = "claude-haiku-4-5"


async def execute() -> None:
    settings = get_settings()
    if not settings.has_anthropic_key or settings.anthropic_api_key is None:
        raise SystemExit("ANTHROPIC_API_KEY is not configured. No paid requests made.")
    SESSION.mkdir(parents=True, exist_ok=True)
    lock = SESSION / "session.lock"
    # A crash intentionally leaves a lock: inspect usage before manually resuming.
    with lock.open("x", encoding="utf-8") as handle:
        handle.write("Exclusive paid session; do not delete while a run is active.\n")
    try:
        await run_session(settings.anthropic_api_key.get_secret_value())
    except BaseException:
        raise  # Keep the lock after an uncertain or interrupted session.
    else:
        lock.unlink()


async def run_session(key: str) -> None:
    pricing = load_pricing(ROOT / "configs/pricing.yaml")
    # Never allow hidden billable retry attempts in this bounded session.
    raw = AnthropicProvider(key, max_retries=0, timeout_seconds=90)
    guard = BudgetedProvider(raw, pricing, SESSION / "budget.json")
    provider = CachedProvider(guard, ROOT / "data/cache/live-validation")
    items, version = load_eval_set(ROOT / "eval_sets", "v1")
    pilot = [items[0], items[8], items[16], next(i for i in items if not i.answerable)]
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    phases = [("pilot", "bm25_only", pilot)] + [
        (name, name, items) for name in ("bm25_only", "vector_only", "hybrid", "hybrid_rerank")
    ]
    for phase, name, selected in phases:
        provider.hits = 0
        provider.misses = 0
        destination = EVIDENCE / phase
        if destination.exists():
            raise RuntimeError(f"Evidence already exists for {phase}; inspect before resuming")
        config = load_run_config(ROOT / f"configs/{name}.yaml").model_copy(
            update={
                "name": f"live_{phase}",
                "generation": GenerationConfig(model=GENERATOR, max_tokens=1536),
                "judge": JudgeConfig(model=JUDGE, max_tokens=1536),
            }
        )
        retriever = load_retriever(config.retrieval, DATASET)
        runner = EvalRunner(
            config=config,
            items=selected,
            dataset_dir=DATASET,
            retriever=retriever,
            run_dir=ROOT / "experiments/runs" / make_run_id(config.name),
            eval_set_name="v1",
            eval_set_version=version,
            provider=provider,
            cache=provider,
            generator_model=GENERATOR,
            judge_model=JUDGE,
            pricing=pricing,
            repo_dir=ROOT,
        )
        runner.retrieve_all()
        print(
            f"Starting {phase}: {len(selected)} questions; "
            f"committed ${guard.ledger.committed_usd:.4f}"
        )
        await runner.generate_all()
        summary = runner.finalize()
        shutil.copytree(runner.run_dir, destination)
        shutil.copy2(guard.path, EVIDENCE / "budget.json")
        print(f"Finished {phase}: errors={summary.n_errors}; ${guard.ledger.committed_usd:.4f}")
        if summary.n_errors:
            raise RuntimeError(
                "Stopping after incomplete phase; preserve results and inspect errors"
            )
    search = load_retriever(load_run_config(ROOT / "configs/bm25_only.yaml").retrieval, DATASET)
    agent_dir = SESSION / "agents"
    agent_dir.mkdir(exist_ok=True)
    agent_records = []
    # Demonstrations only: one attempt each, no pass@k or human-verified success claim.
    for item in pilot:
        trajectory = await run_agent(
            item.question,
            provider=provider,
            search=search,
            model=GENERATOR,
            dataset_version=DATASET.name,
            config=AgentConfig(max_steps=5, max_output_tokens=768, output_token_budget=3072),
        )
        target = agent_dir / f"{item.id}.json"
        target.write_text(trajectory.model_dump_json(indent=2), encoding="utf-8")
        (EVIDENCE / "agents").mkdir(exist_ok=True)
        shutil.copy2(target, EVIDENCE / "agents" / target.name)
        agent_records.append({"item_id": item.id, "stop_reason": trajectory.stop_reason})
        shutil.copy2(guard.path, EVIDENCE / "budget.json")
        if any(step.error for step in trajectory.steps):
            raise RuntimeError("Agent error; inspect saved trajectory before further spend")
    (EVIDENCE / "completion.json").write_text(
        json.dumps(
            {"status": "completed", "agents": agent_records, "human_review": "pending"},
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    if not args.execute:
        parser.exit(
            message="Plan: four-question pilot, four 24-question runs, four agent demos.\n"
            "Shared $3 maximum dispatch budget; real credentials and --execute required.\n"
        )
    os.environ.setdefault("HF_HUB_OFFLINE", "1")
    os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
    asyncio.run(execute())
