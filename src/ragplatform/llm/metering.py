"""Meter every completion attempt, including cached and malformed responses."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import BaseModel, ConfigDict

from ragplatform.models import TokenUsage

if TYPE_CHECKING:
    from ragplatform.llm.pricing import Pricing
    from ragplatform.llm.provider import CompletionRequest, CompletionResponse, LLMProvider


class CallRecord(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    model: str
    purpose: str
    cached: bool = False
    usage: TokenUsage | None = None
    error: str | None = None


class MeteredProvider:
    """Observe the completion boundary, before structured parsing can fail.

    Returned usage is associated with the requested model's configured rate.
    Cache hits retain logical token usage but add no estimated incremental cost.
    Provider exceptions have unknown usage, so total cost is reported as unknown.
    This is accounting, not a spending cap or an invoice reconciliation system.
    """

    def __init__(self, inner: LLMProvider) -> None:
        self.inner = inner
        self.records: list[CallRecord] = []

    @property
    def name(self) -> str:
        return self.inner.name

    async def complete(self, request: CompletionRequest) -> CompletionResponse:
        try:
            response = await self.inner.complete(request)
        except BaseException as exc:
            self.records.append(
                CallRecord(model=request.model, purpose=request.purpose, error=type(exc).__name__)
            )
            raise
        self.records.append(
            CallRecord(
                model=request.model,
                purpose=request.purpose,
                cached=response.cached,
                usage=response.usage,
            )
        )
        return response

    def usage_by_model(self, *, billable_only: bool = False) -> dict[str, TokenUsage]:
        values: dict[str, TokenUsage] = {}
        for record in self.records:
            if record.usage is None or (billable_only and record.cached):
                continue
            values[record.model] = (
                values.get(record.model, TokenUsage(input_tokens=0, output_tokens=0)) + record.usage
            )
        return values

    def estimated_cost(self, pricing: Pricing | None) -> float | None:
        if any(record.usage is None for record in self.records):
            return None
        billable = self.usage_by_model(billable_only=True)
        if not billable:
            return 0.0
        if pricing is None:
            return None
        try:
            return sum(pricing.cost_usd(model, usage) for model, usage in billable.items())
        except KeyError:
            return None
