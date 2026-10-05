"""Offline agent replay with real local BM25 search and scripted decisions."""

import asyncio
import json
from pathlib import Path
from typing import Annotated

import typer

from ragplatform.agent.loop import run_agent
from ragplatform.agent.models import AgentConfig
from ragplatform.cli.retrieval_cmds import resolve_dataset_dir
from ragplatform.ingestion.dataset import read_manifest
from ragplatform.llm.fake import FakeProvider
from ragplatform.llm.provider import CompletionRequest
from ragplatform.retrieval.config import RetrievalConfig
from ragplatform.retrieval.index import load_retriever


def agent_demo(
    question: Annotated[str, typer.Argument()],
    output: Annotated[Path, typer.Option()] = Path("experiments/agent-demo.json"),
    dataset_version: Annotated[str | None, typer.Option()] = None,
    rewrite: Annotated[str | None, typer.Option(help="Optional scripted second search.")] = None,
) -> None:
    """Save a PLACEHOLDER trajectory; never constructs a paid provider."""
    if output.exists():
        raise typer.BadParameter("output already exists; choose a new path")
    directory = resolve_dataset_dir(dataset_version)
    retriever = load_retriever(RetrievalConfig(mode="bm25", rerank=False), directory)
    queries = [question] + ([rewrite] if rewrite else [])

    def responder(request: CompletionRequest) -> str:
        payload = json.loads(request.messages[0].content)
        if len(payload["prior_queries"]) < len(queries):
            return json.dumps({"action": "search", "query": queries[len(payload["prior_queries"])]})
        if not payload["evidence"]:
            return json.dumps({"action": "abstain"})
        return json.dumps(
            {
                "action": "answer",
                "answer": "Placeholder for plumbing verification.",
                "citations": [payload["evidence"][0]["id"]],
            }
        )

    run = asyncio.run(
        run_agent(
            question,
            provider=FakeProvider(responder=responder),
            search=retriever,
            model="fake-model",
            dataset_version=read_manifest(directory).dataset_version,
            config=AgentConfig(),
        )
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(run.model_dump_json(indent=2) + "\n", encoding="utf-8")
    typer.echo(f"PLACEHOLDER: {run.stop_reason}; {len(run.steps)} steps; zero paid calls; {output}")
