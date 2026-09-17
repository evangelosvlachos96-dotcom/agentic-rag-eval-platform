"""Generation: grounded answers with citations and abstention (Milestone 4).

- ``generator``: build the XML context prompt, call the provider through the
  structured-output helper, validate citations, abstain on empty retrieval
"""

from ragplatform.generation.generator import (
    ABSTAIN_TEXT,
    LLMAnswerOutput,
    build_user_message,
    format_context,
    generate_answer,
    validate_citations,
)

__all__ = [
    "ABSTAIN_TEXT",
    "LLMAnswerOutput",
    "build_user_message",
    "format_context",
    "generate_answer",
    "validate_citations",
]
