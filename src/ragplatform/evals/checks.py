"""Programmatic generation checks: what code can verify, code verifies.

These run before any LLM judge and never call a model:

- citation validity: every cited id named a provided chunk (the generator
  already removed invalid ones and recorded them)
- answered without citations: a non-abstaining answer that cites nothing
- correct abstention: the item is unanswerable and the system abstained
- missed abstention: the item is unanswerable but the system answered
- unnecessary abstention: the item is answerable but the system abstained
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import BaseModel, ConfigDict

if TYPE_CHECKING:
    from ragplatform.evals.models import EvalItem
    from ragplatform.models import Answer


class ProgrammaticChecks(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    abstained: bool
    n_citations: int
    n_invalid_citations: int
    citations_valid: bool
    answered_without_citations: bool
    correct_abstention: bool
    missed_abstention: bool
    unnecessary_abstention: bool


def programmatic_checks(answer: Answer, item: EvalItem) -> ProgrammaticChecks:
    abstained = answer.abstained
    return ProgrammaticChecks(
        abstained=abstained,
        n_citations=len(answer.citations),
        n_invalid_citations=len(answer.invalid_citations),
        citations_valid=not answer.invalid_citations,
        answered_without_citations=not abstained and not answer.citations,
        correct_abstention=(not item.answerable) and abstained,
        missed_abstention=(not item.answerable) and not abstained,
        unnecessary_abstention=item.answerable and abstained,
    )
