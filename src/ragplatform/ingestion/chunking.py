"""Structure-aware chunking under a token budget.

Algorithm, in order of preference:

1. Split on section headings (done by the loader; each :class:`Section` is
   chunked independently so a chunk never straddles two sections).
2. Inside a section, split into paragraphs (blank-line separated). Any paragraph
   over the budget is split into sentences; any sentence still over the budget
   is split into groups of words. Words are never split.
3. Pack consecutive units greedily into windows that fit the budget. Each new
   window starts with the last units of the previous one, up to
   ``overlap_ratio * max_tokens`` tokens, so context is not cut mid-thought.

Every chunk records ``char_start``/``char_end`` into the document content, so
``document.content[char_start:char_end] == chunk.content`` always holds.

With ``contextual_header`` enabled, :func:`index_text` returns the text used for
embedding and BM25: ``"<doc title> > <section path>"`` followed by the chunk
text. The chunk's ``content`` stays the original text for display and generation.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, Any

from pydantic import BaseModel, ConfigDict, Field

from ragplatform.ingestion.tokens import ApproxTokenCounter, TokenCounter
from ragplatform.models import Chunk

if TYPE_CHECKING:
    from ragplatform.ingestion.loaders import ParsedDocument, Section

_PARAGRAPH_BREAK = re.compile(r"\n[ \t]*\n")
_SENTENCE_BREAK = re.compile(r"(?<=[.!?])\s+")
_WORD_BREAK = re.compile(r"\s+")

SECTION_SEPARATOR = " > "


class ChunkingConfig(BaseModel):
    """Chunker parameters. Part of the dataset version hash."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    max_tokens: int = Field(default=400, ge=1, description="Token budget per chunk.")
    overlap_ratio: float = Field(
        default=0.15, ge=0.0, lt=1.0, description="Fraction of max_tokens carried over."
    )
    contextual_header: bool = Field(
        default=True, description="Prefix index text with 'doc title > section path'."
    )

    @property
    def overlap_tokens(self) -> int:
        return int(self.max_tokens * self.overlap_ratio)


class ChunkMetadata(BaseModel):
    """Typed view of ``Chunk.metadata`` as written by the chunker."""

    model_config = ConfigDict(frozen=True, extra="ignore")

    doc_title: str
    section_path: str = Field(description='Headings joined by " > "; empty for the preamble.')
    char_start: int = Field(ge=0)
    char_end: int = Field(ge=0)
    token_count: int = Field(ge=0)
    context_header: str | None = Field(
        default=None, description="Prefix for index text when contextual headers are on."
    )
    source: str | None = None

    @classmethod
    def from_chunk(cls, chunk: Chunk) -> ChunkMetadata:
        return cls.model_validate(chunk.metadata)

    def to_dict(self) -> dict[str, Any]:
        return self.model_dump()


class _Span(BaseModel):
    """Internal: a text unit with offsets into the document content."""

    model_config = ConfigDict(frozen=True)

    start: int
    end: int


def _trim(content: str, start: int, end: int) -> tuple[int, int]:
    """Shrink ``[start, end)`` so it excludes leading and trailing whitespace."""
    while start < end and content[start].isspace():
        start += 1
    while end > start and content[end - 1].isspace():
        end -= 1
    return start, end


def _split(content: str, span: _Span, pattern: re.Pattern[str]) -> list[_Span]:
    """Split a span on a regex, returning trimmed non-empty sub-spans."""
    parts: list[_Span] = []
    cursor = span.start
    for match in pattern.finditer(content, span.start, span.end):
        start, end = _trim(content, cursor, match.start())
        if end > start:
            parts.append(_Span(start=start, end=end))
        cursor = match.end()
    start, end = _trim(content, cursor, span.end)
    if end > start:
        parts.append(_Span(start=start, end=end))
    return parts


def _group_words(content: str, span: _Span, counter: TokenCounter, max_tokens: int) -> list[_Span]:
    """Last resort for an over-long sentence: greedy groups of whole words."""
    words = _split(content, span, _WORD_BREAK)
    groups: list[_Span] = []
    i = 0
    while i < len(words):
        j = i + 1
        while (
            j < len(words) and counter.count(content[words[i].start : words[j].end]) <= max_tokens
        ):
            j += 1
        groups.append(_Span(start=words[i].start, end=words[j - 1].end))
        i = j
    return groups


def _units(content: str, section: _Span, counter: TokenCounter, max_tokens: int) -> list[_Span]:
    """Coarsest units that fit the budget: paragraphs, else sentences, else word groups."""
    units: list[_Span] = []
    for paragraph in _split(content, section, _PARAGRAPH_BREAK):
        if counter.count(content[paragraph.start : paragraph.end]) <= max_tokens:
            units.append(paragraph)
            continue
        for sentence in _split(content, paragraph, _SENTENCE_BREAK):
            if counter.count(content[sentence.start : sentence.end]) <= max_tokens:
                units.append(sentence)
            else:
                units.extend(_group_words(content, sentence, counter, max_tokens))
    return units


def _pack(
    content: str, units: list[_Span], counter: TokenCounter, max_tokens: int, overlap_tokens: int
) -> list[_Span]:
    """Greedy windows over consecutive units, each starting with an overlap from the last."""
    windows: list[_Span] = []
    i = 0
    while i < len(units):
        j = i + 1
        while (
            j < len(units) and counter.count(content[units[i].start : units[j].end]) <= max_tokens
        ):
            j += 1
        windows.append(_Span(start=units[i].start, end=units[j - 1].end))
        if j >= len(units):
            break
        # Step back over trailing units that fit the overlap budget, but always advance.
        k = j
        while k - 1 > i and counter.count(content[units[k - 1].start : units[j - 1].end]) <= (
            overlap_tokens
        ):
            k -= 1
        i = k
    return windows


def section_path_string(section: Section) -> str:
    return SECTION_SEPARATOR.join(section.path)


def context_header(doc_title: str, section_path: str) -> str:
    return f"{doc_title}{SECTION_SEPARATOR}{section_path}" if section_path else doc_title


def chunk_document(
    parsed: ParsedDocument,
    config: ChunkingConfig | None = None,
    counter: TokenCounter | None = None,
) -> list[Chunk]:
    """Chunk a parsed document; chunk ids are ``<doc_id>-<position>``."""
    config = config or ChunkingConfig()
    counter = counter or ApproxTokenCounter()
    content = parsed.document.content
    chunks: list[Chunk] = []
    for section in parsed.sections:
        start, end = _trim(content, section.char_start, section.char_end)
        if start >= end:
            continue
        units = _units(content, _Span(start=start, end=end), counter, config.max_tokens)
        windows = _pack(content, units, counter, config.max_tokens, config.overlap_tokens)
        path = section_path_string(section)
        for window in windows:
            text = content[window.start : window.end]
            position = len(chunks)
            metadata = ChunkMetadata(
                doc_title=parsed.title,
                section_path=path,
                char_start=window.start,
                char_end=window.end,
                token_count=counter.count(text),
                context_header=(
                    context_header(parsed.title, path) if config.contextual_header else None
                ),
                source=parsed.document.source,
            )
            chunks.append(
                Chunk(
                    id=f"{parsed.document.id}-{position:04d}",
                    document_id=parsed.document.id,
                    content=text,
                    index=position,
                    metadata=metadata.to_dict(),
                )
            )
    return chunks


def index_text(chunk: Chunk) -> str:
    """Text used for embedding and BM25: the contextual header (if any) plus the content."""
    header = chunk.metadata.get("context_header")
    if isinstance(header, str) and header:
        return f"{header}\n\n{chunk.content}"
    return chunk.content
