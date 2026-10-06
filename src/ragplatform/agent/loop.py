"""Provider-independent search loop; no hidden repair calls or automatic retries."""

from __future__ import annotations

import asyncio
import json
from typing import TYPE_CHECKING, Protocol

from ragplatform.agent.models import AgentAction, AgentConfig, AgentRun, AgentStep
from ragplatform.generation.generator import validate_citations
from ragplatform.llm.provider import CompletionRequest
from ragplatform.llm.structured import parse_as
from ragplatform.models import Answer, RetrievedChunk, TokenUsage
from ragplatform.prompts import load_prompt

if TYPE_CHECKING:
    from ragplatform.llm.provider import LLMProvider


class SearchTool(Protocol):
    def retrieve(self, query: str) -> list[RetrievedChunk]: ...


async def run_agent(
    question: str,
    *,
    provider: LLMProvider,
    search: SearchTool,
    model: str,
    dataset_version: str,
    config: AgentConfig | None = None,
) -> AgentRun:
    """Run bounded actions. Only a validated, cited answer can succeed.

    The output budget bounds the sum of requested completion tokens. Input size
    is bounded separately by question/context characters; it is not a dollar cap.
    Timed-out local search threads may finish in the background, without LLM calls.
    """
    config = config or AgentConfig()
    if not question.strip() or len(question) > config.max_question_chars:
        raise ValueError("Question must be nonempty and within the configured length limit")
    evidence: dict[str, RetrievedChunk] = {}
    queries: list[str] = []
    steps: list[AgentStep] = []
    usage = TokenUsage(input_tokens=0, output_tokens=0)
    remaining = config.output_token_budget
    reason = "step_limit"
    final: AgentAction | None = None
    for number in range(1, config.max_steps + 1):
        if remaining <= 0:
            reason = "output_budget"
            break
        payload = json.dumps(
            {
                "question": question,
                "prior_queries": queries,
                "evidence": [
                    {"id": key, "text": value.chunk.content} for key, value in evidence.items()
                ],
            }
        )
        limit = min(config.max_output_tokens, remaining)
        remaining -= limit  # Reserve the entire allowance, including failed calls.
        request = CompletionRequest.single_turn(
            model=model,
            system=load_prompt(config.prompt_version),
            user=payload,
            purpose="agent",
            max_tokens=limit,
        )
        raw = ""
        action = None
        found: list[RetrievedChunk] = []
        step_usage = TokenUsage(input_tokens=0, output_tokens=0)
        error = None
        try:
            response = await asyncio.wait_for(provider.complete(request), config.timeout_seconds)
            raw = response.text
            step_usage = response.usage
            usage = usage + step_usage
            action = parse_as(raw, AgentAction)
            if action.action == "search":
                query = " ".join(action.query.split())
                if query.casefold() in {q.casefold() for q in queries}:
                    reason = "repeated_query"
                    break
                queries.append(query)
                found = await asyncio.wait_for(
                    asyncio.to_thread(search.retrieve, query), config.timeout_seconds
                )
                # Keep whole chunks only. Never expose a citation for omitted evidence.
                for item in found:
                    if item.chunk.id in evidence or len(evidence) >= config.max_chunks:
                        continue
                    trial = {**evidence, item.chunk.id: item}
                    context = json.dumps(
                        [{"id": k, "text": v.chunk.content} for k, v in trial.items()]
                    )
                    if len(context) <= config.max_context_chars:
                        evidence[item.chunk.id] = item
            elif action.action == "abstain":
                reason = "abstained"
                break
            else:
                valid, invalid = validate_citations(action.citations, set(evidence))
                if invalid or not valid:
                    reason = "invalid_citations"
                    break
                final = action
                reason = "answered"
                break
        except (ValueError, RuntimeError, TimeoutError, OSError) as exc:
            # Record failures without a silent extra completion or an invented answer.
            error = type(exc).__name__
            reason = "error"
            break
        finally:
            steps.append(
                AgentStep(
                    number=number,
                    request=payload,
                    raw_response=raw,
                    action=action,
                    retrieved=found,
                    usage=step_usage,
                    error=error,
                )
            )
    citations, invalid = validate_citations(final.citations if final else [], set(evidence))
    answer = Answer(
        query=question,
        text=final.answer if final else "",
        citations=citations,
        abstained=final is None,
        model=model,
        prompt_version=config.prompt_version,
        usage=usage,
        invalid_citations=invalid,
        metadata={"stop_reason": reason},
    )
    return AgentRun(
        question=question,
        config=config,
        provider=provider.name,
        model=model,
        dataset_version=dataset_version,
        placeholder="fake" in provider.name,
        stop_reason=reason,
        steps=steps,
        answer=answer,
        usage=usage,
    )
