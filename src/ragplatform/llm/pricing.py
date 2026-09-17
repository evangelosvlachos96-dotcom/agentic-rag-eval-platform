"""Model prices from ``configs/pricing.yaml`` and cost estimates from token counts.

Prices are configuration, not code: the YAML lists USD per million input and
output tokens per model id, with the date they were checked. Unknown models
raise so a run never reports a silently wrong cost.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import yaml
from pydantic import BaseModel, ConfigDict, Field

if TYPE_CHECKING:
    from pathlib import Path

    from ragplatform.models import TokenUsage


class ModelPrice(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    input_per_mtok: float = Field(ge=0)
    output_per_mtok: float = Field(ge=0)


class Pricing(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    checked_on: str = Field(description="Date the prices were last verified (ISO date).")
    source: str = Field(description="Where the prices came from.")
    models: dict[str, ModelPrice]

    def price_for(self, model: str) -> ModelPrice:
        try:
            return self.models[model]
        except KeyError:
            known = ", ".join(sorted(self.models))
            raise KeyError(f"no price for model {model!r}; known: {known}") from None

    def cost_usd(self, model: str, usage: TokenUsage) -> float:
        price = self.price_for(model)
        return (
            usage.input_tokens * price.input_per_mtok + usage.output_tokens * price.output_per_mtok
        ) / 1_000_000


def load_pricing(path: Path) -> Pricing:
    return Pricing.model_validate(yaml.safe_load(path.read_text(encoding="utf-8")))
