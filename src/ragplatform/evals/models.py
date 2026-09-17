"""Evaluation item schema.

Relevance is labeled by *source* (``doc_id`` + ``section_path``), never by chunk
id: chunk ids change whenever the chunker's parameters change, section paths
do not. A retrieved chunk counts as relevant when its document matches and its
section path equals, or is nested under, a labeled section path (an empty
labeled path means "anywhere in the document").
"""

from __future__ import annotations

from typing import Literal, get_args

from pydantic import BaseModel, ConfigDict, Field, model_validator

Category = Literal["lookup", "conceptual", "exact_term", "multi_hop", "comparison", "unanswerable"]
Difficulty = Literal["easy", "medium", "hard"]
CreatedBy = Literal["human", "synthetic_reviewed"]

CATEGORIES: tuple[str, ...] = get_args(Category)
ANSWERABLE_CATEGORIES: tuple[str, ...] = tuple(c for c in CATEGORIES if c != "unanswerable")


class SourceRef(BaseModel):
    """A labeled relevant location: a document and a heading path inside it."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    doc_id: str = Field(min_length=1)
    section_path: str = Field(
        default="", description='Heading path such as "Specification > Syntax"; "" = whole doc.'
    )


class EvalItem(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    id: str = Field(min_length=1)
    question: str = Field(min_length=1)
    reference_answer: str = Field(min_length=1)
    relevant_sources: list[SourceRef] = Field(default_factory=list)
    category: Category
    difficulty: Difficulty = "medium"
    answerable: bool = True
    created_by: CreatedBy
    notes: str = ""

    @model_validator(mode="after")
    def _consistent(self) -> EvalItem:
        if (self.category == "unanswerable") != (not self.answerable):
            raise ValueError("category 'unanswerable' must match answerable=False")
        if self.answerable and not self.relevant_sources:
            raise ValueError("answerable items need at least one relevant source")
        return self
