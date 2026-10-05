"""Local FastAPI service; provider injection is required for any generation."""

from __future__ import annotations

import asyncio
import os
from pathlib import Path
from typing import TYPE_CHECKING, Literal

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict, Field

from ragplatform.agent.loop import SearchTool, run_agent
from ragplatform.agent.models import AgentConfig, AgentRun
from ragplatform.generation.generator import generate_answer
from ragplatform.models import Answer, RetrievedChunk
from ragplatform.observability.tracing import span, trace
from ragplatform.pipelines.run_config import GenerationConfig

if TYPE_CHECKING:
    from ragplatform.llm.provider import LLMProvider


class QueryRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    question: str = Field(min_length=1, max_length=4000)
    mode: Literal["retrieve", "answer", "agent"] = "retrieve"


class QueryResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    trace_id: str
    dataset_version: str
    placeholder: bool
    retrieved: list[RetrievedChunk] = Field(default_factory=list)
    answer: Answer | None = None
    agent: AgentRun | None = None


def create_app(
    search: SearchTool | None = None,
    *,
    dataset_version: str = "unconfigured",
    provider: LLMProvider | None = None,
    model: str = "fake-model",
    concurrency: int = 2,
    timeout_seconds: float = 60,
) -> FastAPI:
    """Factory for local deployment and dependency-injected offline tests."""
    if concurrency < 1 or timeout_seconds <= 0:
        raise ValueError("Concurrency and timeout must be positive")
    app = FastAPI(title="Agentic RAG evaluation platform", version="0.1.0")
    slots = asyncio.Semaphore(concurrency)
    counts = {"queries": 0, "completed": 0, "errors": 0}

    @app.get("/health")
    async def health() -> dict[str, str | bool]:
        return {
            "ready": search is not None,
            "dataset_version": dataset_version,
            "generation_enabled": provider is not None,
        }

    @app.get("/metrics")
    async def metrics() -> dict[str, int]:
        return dict(counts)

    @app.post("/query")
    async def query(request: QueryRequest) -> QueryResponse:
        counts["queries"] += 1
        with trace() as correlation:
            try:
                if search is None:
                    raise HTTPException(503, "No local dataset configured")
                if request.mode != "retrieve" and provider is None:
                    raise HTTPException(403, "Generation disabled; inject a provider explicitly")
                async with asyncio.timeout(timeout_seconds), slots:
                    if request.mode == "agent":
                        if provider is None:
                            raise HTTPException(403, "Generation disabled")
                        with span("agent"):
                            run = await run_agent(
                                request.question,
                                provider=provider,
                                search=search,
                                model=model,
                                dataset_version=dataset_version,
                                config=AgentConfig(),
                            )
                        response = QueryResponse(
                            trace_id=correlation,
                            dataset_version=dataset_version,
                            placeholder=run.placeholder,
                            answer=run.answer,
                            agent=run,
                        )
                    else:
                        with span("retrieval"):
                            retrieved = await asyncio.to_thread(search.retrieve, request.question)
                        answer = None
                        if request.mode == "answer" and provider is not None:
                            with span("generation"):
                                answer = await generate_answer(
                                    request.question, retrieved, provider, GenerationConfig(), model
                                )
                        response = QueryResponse(
                            trace_id=correlation,
                            dataset_version=dataset_version,
                            placeholder=provider is not None and provider.name == "fake",
                            retrieved=retrieved,
                            answer=answer,
                        )
                counts["completed"] += 1
                return response
            except HTTPException:
                counts["errors"] += 1
                raise
            except TimeoutError as exc:
                counts["errors"] += 1
                raise HTTPException(504, "Query timed out") from exc
            except Exception as exc:
                counts["errors"] += 1
                raise HTTPException(500, "Query failed; inspect server logs") from exc

    return app


def local_app() -> FastAPI:
    """Uvicorn factory. Always retrieval-only; never reads or instantiates API keys."""
    from ragplatform.ingestion.dataset import read_manifest
    from ragplatform.retrieval.config import RetrievalConfig
    from ragplatform.retrieval.index import load_retriever

    directory = os.environ.get("RAG_DATASET_DIR")
    if directory is None:
        return create_app()
    path = Path(directory)
    return create_app(
        load_retriever(RetrievalConfig(mode="bm25", rerank=False), path),
        dataset_version=read_manifest(path).dataset_version,
    )
