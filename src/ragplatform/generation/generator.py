"""Grounded answer generation with citations and abstention.

Flow for one question:

1. No retrieved chunks -> abstain immediately, no LLM call.
2. Build the user message: every chunk in an XML block with its id, then the
   question. The system prompt is the versioned file named by the config.
3. Ask for a JSON object, validate it as :class:`LLMAnswerOutput` (one repair
   retry via :func:`complete_structured`).
4. Programmatic checks: citations that do not name a provided chunk id are
   removed and recorded in ``Answer.invalid_citations``. A non-abstaining answer
   with no valid citations is *not* turned into an abstention here; the eval
   harness flags it, so the failure stays visible.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import BaseModel, ConfigDict, Field

from ragplatform.ingestion.chunking import ChunkMetadata
from ragplatform.llm.provider import ChatMessage, CompletionRequest
from ragplatform.llm.structured import complete_structured
from ragplatform.models import Answer, Citation, RetrievedChunk
from ragplatform.prompts import load_prompt

if TYPE_CHECKING:
    from collections.abc import Sequence

    from ragplatform.llm.provider import LLMProvider
    from ragplatform.pipelines.run_config import GenerationConfig

ABSTAIN_TEXT = "The retrieved context does not contain enough information to answer this question."


class LLMAnswerOutput(BaseModel):
    """The JSON object the answer prompt asks for."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    answer: str
    citations: list[str] = Field(default_factory=list)
    abstain: bool = False


def format_context(chunks: Sequence[RetrievedChunk]) -> str:
    """XML-delimited chunk blocks, each tagged with its id and section for the model."""
    blocks: list[str] = []
    for retrieved in chunks:
        chunk = retrieved.chunk
        meta = ChunkMetadata.from_chunk(chunk)
        where = f"{meta.doc_title} > {meta.section_path}" if meta.section_path else meta.doc_title
        blocks.append(f'<chunk id="{chunk.id}" source="{where}">\n{chunk.content}\n</chunk>')
    return "\n\n".join(blocks)


def build_user_message(question: str, chunks: Sequence[RetrievedChunk]) -> str:
    return f"<context>\n{format_context(chunks)}\n</context>\n\n<question>\n{question}\n</question>"


def validate_citations(
    cited: Sequence[str], provided_ids: set[str]
) -> tuple[list[Citation], list[str]]:
    """Split cited ids into valid citations (deduplicated, in order) and invalid ids."""
    valid: list[Citation] = []
    invalid: list[str] = []
    seen: set[str] = set()
    for chunk_id in cited:
        if chunk_id in seen:
            continue
        seen.add(chunk_id)
        if chunk_id in provided_ids:
            valid.append(Citation(chunk_id=chunk_id))
        else:
            invalid.append(chunk_id)
    return valid, invalid


async def generate_answer(
    question: str,
    chunks: Sequence[RetrievedChunk],
    provider: LLMProvider,
    config: GenerationConfig,
    model: str,
) -> Answer:
    """Answer ``question`` from ``chunks`` only; abstain without an LLM call when empty."""
    if not chunks:
        return Answer(
            query=question,
            text=ABSTAIN_TEXT,
            abstained=True,
            prompt_version=config.prompt_version,
            model=None,
            metadata={"reason": "empty_retrieval"},
        )

    request = CompletionRequest(
        model=model,
        system=load_prompt(config.prompt_version),
        messages=[ChatMessage(role="user", content=build_user_message(question, chunks))],
        max_tokens=config.max_tokens,
        purpose="answer",
    )
    output, result = await complete_structured(provider, request, LLMAnswerOutput)
    provided_ids = {retrieved.chunk.id for retrieved in chunks}
    citations, invalid = validate_citations(output.citations, provided_ids)
    if output.abstain:
        citations = []
    return Answer(
        query=question,
        text=output.answer,
        citations=citations,
        abstained=output.abstain,
        model=result.model,
        prompt_version=config.prompt_version,
        usage=result.usage,
        invalid_citations=invalid,
        metadata={"repaired": result.repaired, "n_context_chunks": len(chunks)},
    )
