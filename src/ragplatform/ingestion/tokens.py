"""Token counting behind a small interface.

The chunker only needs "how many tokens is this text", so it depends on the
:class:`TokenCounter` protocol rather than on any tokenizer library. The
default :class:`ApproxTokenCounter` uses the common rule of thumb of about four
characters per token for English prose, which is good enough for sizing
chunks and needs no model download. A tokenizer-backed counter can be dropped
in later without touching the chunker.
"""

from __future__ import annotations

import math
from typing import Protocol


class TokenCounter(Protocol):
    """Counts tokens in a piece of text."""

    def count(self, text: str) -> int: ...


class ApproxTokenCounter:
    """Approximate token count: ``ceil(len(text) / chars_per_token)``, 0 for empty text."""

    def __init__(self, chars_per_token: float = 4.0) -> None:
        if chars_per_token <= 0:
            raise ValueError("chars_per_token must be positive")
        self.chars_per_token = chars_per_token

    def count(self, text: str) -> int:
        if not text:
            return 0
        return max(1, math.ceil(len(text) / self.chars_per_token))
