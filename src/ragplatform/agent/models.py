"""Bounded agent contracts and replayable trajectories."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from ragplatform.models import Answer, RetrievedChunk, TokenUsage


class AgentConfig(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    max_steps: int = Field(default=5, ge=1, le=30)
    max_output_tokens: int = Field(default=512, ge=1)
    output_token_budget: int = Field(default=2048, ge=1)
    max_context_chars: int = Field(default=24000, ge=100)
    max_question_chars: int = Field(default=4000, ge=1)
    max_chunks: int = Field(default=16, ge=1)
    timeout_seconds: float = Field(default=60, gt=0)
    prompt_version: str = "agent_v1"


class AgentAction(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    action: Literal["search", "answer", "abstain"]
    query: str = Field(default="", max_length=2000)
    answer: str = ""
    citations: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def coherent(self) -> AgentAction:
        if self.action == "search" and (not self.query.strip() or self.answer or self.citations):
            raise ValueError("search requires a query and no answer or citations")
        if self.action == "answer" and (
            not self.answer.strip() or not self.citations or self.query
        ):
            raise ValueError("answer requires text and citations, with no query")
        if self.action == "abstain" and (self.query or self.answer or self.citations):
            raise ValueError("abstain has no other fields")
        return self


class AgentStep(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    number: int
    request: str
    raw_response: str = ""
    action: AgentAction | None = None
    retrieved: list[RetrievedChunk] = Field(default_factory=list)
    usage: TokenUsage = Field(default_factory=lambda: TokenUsage(input_tokens=0, output_tokens=0))
    error: str | None = None


class AgentRun(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    question: str
    config: AgentConfig
    provider: str
    model: str
    dataset_version: str
    placeholder: bool
    stop_reason: str
    steps: list[AgentStep]
    answer: Answer
    usage: TokenUsage
