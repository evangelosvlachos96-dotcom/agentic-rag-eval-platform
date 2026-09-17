"""BM25 lexical retrieval over chunk index text (``rank_bm25``).

Tokenizer: the text is lower-cased and split into runs of letters, digits and
underscores that may be joined by ``-`` or ``.``. So ``PEP-484`` becomes the
single token ``pep-484`` and ``__future__`` stays ``__future__``. Compound
tokens are indexed both whole *and* as their parts (``pep-484`` -> ``pep-484``,
``pep``, ``484``), so an exact identifier query matches exactly while prose
that only mentions the parts still matches. The same function tokenizes
queries, which keeps the two sides consistent.

The index is saved as JSON (ids + tokenized texts) and rebuilt on load; no
pickle is involved.
"""

from __future__ import annotations

import json
import re
from typing import TYPE_CHECKING, cast

import numpy as np
from rank_bm25 import BM25Okapi

if TYPE_CHECKING:
    from collections.abc import Sequence
    from pathlib import Path

    from numpy.typing import NDArray

_TOKEN = re.compile(r"[a-z0-9_]+(?:[-.][a-z0-9_]+)*")
_PART = re.compile(r"[a-z0-9_]+")


def tokenize(text: str) -> list[str]:
    """Lower-case tokens; compound identifiers are kept whole and also split into parts."""
    tokens: list[str] = []
    for token in _TOKEN.findall(text.lower()):
        tokens.append(token)
        if "-" in token or "." in token:
            tokens.extend(_PART.findall(token))
    return tokens


class BM25Index:
    """Okapi BM25 over pre-tokenized texts, keyed by chunk id."""

    def __init__(self, ids: Sequence[str], tokenized: Sequence[Sequence[str]]) -> None:
        if len(ids) != len(tokenized):
            raise ValueError("ids and tokenized texts must have the same length")
        if not ids:
            raise ValueError("BM25 index needs at least one document")
        self._ids = list(ids)
        self._tokenized = [list(t) for t in tokenized]
        self._bm25 = BM25Okapi(self._tokenized)

    @classmethod
    def from_texts(cls, ids: Sequence[str], texts: Sequence[str]) -> BM25Index:
        return cls(ids, [tokenize(t) for t in texts])

    def __len__(self) -> int:
        return len(self._ids)

    def search(self, query: str, k: int) -> list[tuple[str, float]]:
        """Top-k ``(id, score)`` with positive BM25 score, best first."""
        if k <= 0:
            return []
        query_tokens = tokenize(query)
        if not query_tokens:
            return []
        scores = cast("NDArray[np.float64]", np.asarray(self._bm25.get_scores(query_tokens)))
        order = np.lexsort((np.arange(len(scores)), -scores))
        results: list[tuple[str, float]] = []
        for i in order[:k]:
            score = float(scores[int(i)])
            if score <= 0.0:
                break
            results.append((self._ids[int(i)], score))
        return results

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = {"ids": self._ids, "tokens": self._tokenized}
        path.write_text(json.dumps(payload), encoding="utf-8")

    @classmethod
    def load(cls, path: Path) -> BM25Index:
        payload = json.loads(path.read_text(encoding="utf-8"))
        return cls(payload["ids"], payload["tokens"])
