"""The question taxonomy: versioned YAML describing every eval category."""

from __future__ import annotations

from typing import TYPE_CHECKING

import yaml
from pydantic import BaseModel, ConfigDict, Field, model_validator

from ragplatform.evals.models import CATEGORIES

if TYPE_CHECKING:
    from pathlib import Path


class CategoryDefinition(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    definition: str = Field(min_length=1)
    decision_rule: str = Field(min_length=1)
    example: str = Field(min_length=1)


class Taxonomy(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    version: str = Field(min_length=1)
    categories: dict[str, CategoryDefinition]

    @model_validator(mode="after")
    def _matches_schema(self) -> Taxonomy:
        expected = set(CATEGORIES)
        actual = set(self.categories)
        if actual != expected:
            raise ValueError(
                f"taxonomy categories {sorted(actual)} must equal schema {sorted(expected)}"
            )
        return self

    def describe(self) -> str:
        """Plain-text rendering used inside prompts."""
        lines: list[str] = []
        for name, definition in self.categories.items():
            lines.append(f"- {name}: {definition.definition} Rule: {definition.decision_rule}")
            lines.append(f"  Example: {definition.example}")
        return "\n".join(lines)


def load_taxonomy(path: Path) -> Taxonomy:
    return Taxonomy.model_validate(yaml.safe_load(path.read_text(encoding="utf-8")))
