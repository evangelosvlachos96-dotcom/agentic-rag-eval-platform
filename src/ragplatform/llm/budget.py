"""Persistent pre-call reservations for a single, sequential paid validation session."""

from __future__ import annotations

import asyncio
import math
from typing import TYPE_CHECKING, Protocol

from pydantic import BaseModel, ConfigDict, Field

from ragplatform.llm.provider import CompletionRequest, CompletionResponse, LLMError, LLMProvider
from ragplatform.models import TokenUsage

if TYPE_CHECKING:
    from pathlib import Path

    from ragplatform.llm.pricing import Pricing


class CountingProvider(LLMProvider, Protocol):
    async def count_input_tokens(self, request: CompletionRequest) -> int: ...


class BudgetStoppedError(LLMError):
    """No request was dispatched because the session cannot safely continue."""


class BudgetRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    model: str
    purpose: str
    reserved_usd: float
    actual_usd: float | None = None
    usage: TokenUsage | None = None
    response_model: str | None = None
    status: str = "reserved"


class BudgetLedger(BaseModel):
    model_config = ConfigDict(extra="forbid")

    limit_usd: float = Field(gt=0, le=3)
    records: list[BudgetRecord] = Field(default_factory=list)

    @property
    def committed_usd(self) -> float:
        return sum(
            r.actual_usd if r.actual_usd is not None else r.reserved_usd for r in self.records
        )


class BudgetedProvider:
    """Count first, reserve before sending, persist usage, stop on uncertain billing.

    The caller must use SDK retries=0 and hold an exclusive session lock. Pricing
    must be verified. This bounds dispatch using buffered token counts and maximum
    output allowances; account taxes/adjustments are not an invoice guarantee.
    """

    def __init__(self, provider: CountingProvider, pricing: Pricing, path: Path) -> None:
        self.provider = provider
        self.pricing = pricing
        self.path = path
        self.ledger = (
            BudgetLedger.model_validate_json(path.read_text(encoding="utf-8"))
            if path.exists()
            else BudgetLedger(limit_usd=3)
        )
        self._lock = asyncio.Lock()
        self._stopped = any(r.status != "completed" for r in self.ledger.records)

    @property
    def name(self) -> str:
        return f"budgeted({self.provider.name})"

    def _save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.path.with_suffix(".tmp")
        temporary.write_text(self.ledger.model_dump_json(indent=2) + "\n", encoding="utf-8")
        temporary.replace(self.path)

    async def complete(self, request: CompletionRequest) -> CompletionResponse:
        async with self._lock:
            if self._stopped:
                raise BudgetStoppedError(
                    "Session stopped; inspect the ledger before any further spend"
                )
            # Unknown models fail before even a token-count request is made.
            self.pricing.price_for(request.model)
            try:
                count = await self.provider.count_input_tokens(request)
            except BaseException:
                self._stopped = True
                raise
            if count < 0:
                raise BudgetStoppedError("Invalid token count")
            allowance = TokenUsage(
                input_tokens=math.ceil(count * 1.2) + 1024,
                output_tokens=request.max_tokens,
            )
            reserve = self.pricing.cost_usd(request.model, allowance)
            if self.ledger.committed_usd + reserve > self.ledger.limit_usd:
                self._stopped = True
                raise BudgetStoppedError(
                    "Insufficient remaining budget for maximum request allowance"
                )
            record = BudgetRecord(
                model=request.model, purpose=request.purpose, reserved_usd=reserve
            )
            self.ledger.records.append(record)
            self._stopped = True  # Also fail closed if persistence fails.
            self._save()  # Persist the reservation BEFORE the billable request.
            try:
                response = await self.provider.complete(request)
            except BaseException:
                self._stopped = True
                record.status = "unknown_usage"
                self._save()
                raise
            record.usage = response.usage
            record.response_model = response.model
            record.actual_usd = self.pricing.cost_usd(request.model, response.usage)
            record.status = "completed"
            if record.actual_usd > reserve:
                self._stopped = True
                record.status = "reservation_exceeded"
            self._save()
            if record.status == "completed":
                self._stopped = False
            return response
