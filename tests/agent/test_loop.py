"""Offline agent behavior, cost boundaries, and evidence validity."""

import json

import pytest

from ragplatform.agent.loop import run_agent
from ragplatform.agent.metrics import pass_at_k, pass_power_k
from ragplatform.agent.models import AgentConfig
from ragplatform.llm.fake import FakeProvider
from ragplatform.models import Chunk, RetrievedChunk


class Search:
    def __init__(self) -> None:
        self.queries: list[str] = []

    def retrieve(self, query: str) -> list[RetrievedChunk]:
        self.queries.append(query)
        return [
            RetrievedChunk(
                chunk=Chunk(id=query, document_id="doc", content="Evidence " + query, index=0),
                score=1,
                rank=1,
                retriever="test",
            )
        ]


@pytest.mark.asyncio
async def test_rewrite_and_cited_answer() -> None:
    provider = FakeProvider(
        responses=[
            '{"action":"search","query":"first"}',
            '{"action":"search","query":"second"}',
            '{"action":"answer","answer":"Both facts","citations":["first","second"]}',
        ]
    )
    search = Search()
    run = await run_agent(
        "question", provider=provider, search=search, model="fake", dataset_version="fixture"
    )
    assert search.queries == ["first", "second"]
    assert run.stop_reason == "answered"
    assert run.placeholder
    assert len(run.answer.citations) == 2
    assert len(run.steps) == 3
    assert json.loads(provider.requests[2].messages[0].content)["prior_queries"] == search.queries
    assert run.usage.output_tokens == sum(step.usage.output_tokens for step in run.steps)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("responses", "reason"),
    [
        (["not json"], "error"),
        (['{"action":"abstain"}'], "abstained"),
        (['{"action":"answer","answer":"invented","citations":["unknown"]}'], "invalid_citations"),
        (
            ['{"action":"search","query":"x"}', '{"action":"search","query":" X "}'],
            "repeated_query",
        ),
    ],
)
async def test_fail_closed(responses: list[str], reason: str) -> None:
    provider = FakeProvider(responses=responses)
    run = await run_agent(
        "q", provider=provider, search=Search(), model="fake", dataset_version="fixture"
    )
    assert run.stop_reason == reason
    assert run.answer.abstained
    assert provider.calls == len(responses)


@pytest.mark.asyncio
async def test_budget_and_step_boundaries() -> None:
    provider = FakeProvider(responses=['{"action":"search","query":"x"}'])
    run = await run_agent(
        "q",
        provider=provider,
        search=Search(),
        model="fake",
        dataset_version="fixture",
        config=AgentConfig(output_token_budget=100),
    )
    assert run.stop_reason == "output_budget"
    assert provider.requests[0].max_tokens == 100
    provider = FakeProvider(responses=['{"action":"search","query":"x"}'])
    run = await run_agent(
        "q",
        provider=provider,
        search=Search(),
        model="fake",
        dataset_version="fixture",
        config=AgentConfig(max_steps=1),
    )
    assert run.stop_reason == "step_limit"
    assert provider.calls == 1


@pytest.mark.asyncio
async def test_omitted_context_cannot_be_cited() -> None:
    large = "a" * 200
    provider = FakeProvider(
        responses=[
            json.dumps({"action": "search", "query": large}),
            json.dumps({"action": "answer", "answer": "text", "citations": [large]}),
        ]
    )
    run = await run_agent(
        "q",
        provider=provider,
        search=Search(),
        model="fake",
        dataset_version="fixture",
        config=AgentConfig(max_context_chars=100),
    )
    assert run.stop_reason == "invalid_citations"
    assert json.loads(provider.requests[-1].messages[0].content)["evidence"] == []


def test_repeated_attempt_metrics() -> None:
    assert pass_at_k(4, 2, 2) == pytest.approx(5 / 6)
    assert pass_power_k(4, 2, 2) == pytest.approx(1 / 6)
    assert pass_at_k(4, 0, 2) == 0
    assert pass_power_k(4, 4, 2) == 1
    with pytest.raises(ValueError, match="Require"):
        pass_at_k(1, 1, 2)


@pytest.mark.asyncio
async def test_timeout_and_question_limit() -> None:
    import asyncio

    from ragplatform.llm.provider import CompletionRequest, CompletionResponse

    class SlowProvider:
        name = "fake"

        async def complete(self, request: CompletionRequest) -> CompletionResponse:
            await asyncio.sleep(10)
            raise AssertionError("must be cancelled")

    run = await run_agent(
        "q",
        provider=SlowProvider(),
        search=Search(),
        model="fake",
        dataset_version="fixture",
        config=AgentConfig(timeout_seconds=0.01),
    )
    assert run.stop_reason == "error"
    assert run.steps[0].error == "TimeoutError"
    provider = FakeProvider(responses=[])
    with pytest.raises(ValueError, match="Question"):
        await run_agent(
            "  ", provider=provider, search=Search(), model="fake", dataset_version="fixture"
        )
    assert provider.calls == 0
