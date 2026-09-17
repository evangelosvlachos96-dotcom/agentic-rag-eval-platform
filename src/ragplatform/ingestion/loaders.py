"""Loaders: parse ``.rst``, ``.md`` and ``.txt`` files into documents with headings.

A loader returns a :class:`ParsedDocument`: the :class:`~ragplatform.models.Document`
(normalized text, stable id, title in metadata) plus an ordered list of
:class:`Section` objects. Each section is a character span of the document
content that lies *under* a heading path such as ``("Specification", "Syntax")``;
the heading lines themselves are not part of any section body. Text before the
first heading is a section with an empty path.

Offsets always index into ``document.content`` so chunks can be mapped back to
the exact source text.
"""

from __future__ import annotations

import hashlib
import re
from typing import TYPE_CHECKING, Protocol

from pydantic import BaseModel, ConfigDict, Field

from ragplatform.models import Document

if TYPE_CHECKING:
    from pathlib import Path

# Characters docutils accepts as section adornment (underline / overline).
_RST_ADORNMENT_CHARS = set("=-`:'\"~^_*+#<>")
_RST_HEADER_FIELD = re.compile(r"^([A-Za-z][A-Za-z0-9-]*):\s?(.*)$")
_MD_HEADING = re.compile(r"^(#{1,6})\s+(.+?)\s*#*\s*$")
_MD_FENCE = re.compile(r"^(```|~~~)")


class Section(BaseModel):
    """A span of document text under a heading path."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    path: tuple[str, ...] = Field(description="Heading hierarchy; empty for the preamble.")
    char_start: int = Field(ge=0)
    char_end: int = Field(ge=0)


class ParsedDocument(BaseModel):
    """A document together with its heading structure."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    document: Document
    title: str = Field(min_length=1)
    sections: list[Section]

    def section_text(self, section: Section) -> str:
        return self.document.content[section.char_start : section.char_end]


class Loader(Protocol):
    """Parses the text of one file format into a :class:`ParsedDocument`."""

    def parse(self, text: str, *, source: str | None, fallback_title: str) -> ParsedDocument: ...


def normalize_text(text: str) -> str:
    """Unify line endings and strip trailing whitespace on every line."""
    lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    return "\n".join(line.rstrip() for line in lines).strip("\n")


def document_id(content: str) -> str:
    """Stable id: the first 16 hex chars of the sha256 of the normalized content."""
    return hashlib.sha256(normalize_text(content).encode("utf-8")).hexdigest()[:16]


def _line_offsets(lines: list[str]) -> list[int]:
    """Character offset at which each line starts (lines are joined by ``\\n``)."""
    offsets: list[int] = []
    pos = 0
    for line in lines:
        offsets.append(pos)
        pos += len(line) + 1
    return offsets


class _Heading(BaseModel):
    """Internal: a heading found while scanning lines."""

    model_config = ConfigDict(frozen=True)

    level: int
    title: str
    first_line: int
    last_line: int


def _build_sections(
    lines: list[str], headings: list[_Heading], content_length: int, body_start_line: int = 0
) -> list[Section]:
    """Turn a flat heading list into sections with hierarchical paths.

    ``level`` is 1 for top-level headings; deeper levels nest under the nearest
    shallower heading that precedes them.
    """
    offsets = _line_offsets(lines)
    sections: list[Section] = []
    stack: list[tuple[int, str]] = []

    def line_start(line_index: int) -> int:
        return offsets[line_index] if line_index < len(lines) else content_length

    first_heading_line = headings[0].first_line if headings else len(lines)
    preamble_start = line_start(body_start_line)
    preamble_end = line_start(first_heading_line)
    if preamble_end > preamble_start:
        sections.append(Section(path=(), char_start=preamble_start, char_end=preamble_end))

    for i, heading in enumerate(headings):
        while stack and stack[-1][0] >= heading.level:
            stack.pop()
        stack.append((heading.level, heading.title))
        body_start = line_start(heading.last_line + 1)
        body_end = (
            line_start(headings[i + 1].first_line) if i + 1 < len(headings) else content_length
        )
        body_end = max(body_end, body_start)
        path = tuple(title for _, title in stack)
        sections.append(Section(path=path, char_start=body_start, char_end=body_end))
    return sections


# --------------------------------------------------------------------------- RST


def _is_adornment(line: str) -> bool:
    return len(line) >= 3 and line[0] in _RST_ADORNMENT_CHARS and line == line[0] * len(line)


def _parse_rst_header_block(lines: list[str]) -> tuple[dict[str, str], int]:
    """Parse an RFC 822 style header block (as used by PEPs) at the top of a file.

    Returns the fields and the index of the first line after the block. If the
    file does not start with a ``Name: value`` line, no header is consumed.
    """
    fields: dict[str, str] = {}
    if not lines or not _RST_HEADER_FIELD.match(lines[0]):
        return fields, 0
    current: str | None = None
    i = 0
    while i < len(lines) and lines[i].strip():
        match = _RST_HEADER_FIELD.match(lines[i])
        if match:
            current = match.group(1)
            fields[current] = match.group(2).strip()
        elif current is not None and lines[i][0].isspace():
            fields[current] = (fields[current] + " " + lines[i].strip()).strip()
        else:
            break
        i += 1
    return fields, i


def _find_rst_headings(lines: list[str], start_line: int) -> list[_Heading]:
    """Detect underlined (optionally overlined) headings, assigning levels by first use."""
    headings: list[_Heading] = []
    styles: dict[str, int] = {}
    i = start_line
    while i < len(lines) - 1:
        title = lines[i]
        underline = lines[i + 1]
        if (
            title.strip()
            and not title[0].isspace()
            and _is_adornment(underline)
            and len(underline) >= len(title)
        ):
            first_line = i
            style = underline[0]
            if i > 0 and lines[i - 1] == underline:
                first_line = i - 1
                style = "over" + style
            level = styles.setdefault(style, len(styles) + 1)
            headings.append(
                _Heading(level=level, title=title.strip(), first_line=first_line, last_line=i + 1)
            )
            i += 2
        else:
            i += 1
    return headings


class RstLoader:
    """reStructuredText: PEP-style header block plus underlined section titles."""

    def parse(self, text: str, *, source: str | None, fallback_title: str) -> ParsedDocument:
        content = normalize_text(text)
        lines = content.split("\n")
        headers, body_start_line = _parse_rst_header_block(lines)
        headings = _find_rst_headings(lines, body_start_line)
        title = headers.get("Title") or (headings[0].title if headings else fallback_title)
        metadata: dict[str, object] = {"title": title, "format": "rst"}
        if headers:
            metadata["headers"] = headers
        document = Document(
            id=document_id(content), content=content, source=source, metadata=metadata
        )
        # The header block is kept as the preamble so its fields stay searchable.
        sections = _build_sections(lines, headings, len(content), body_start_line=0)
        return ParsedDocument(document=document, title=title, sections=sections)


# --------------------------------------------------------------------------- Markdown


def _find_md_headings(lines: list[str]) -> list[_Heading]:
    headings: list[_Heading] = []
    in_fence = False
    for i, line in enumerate(lines):
        if _MD_FENCE.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        match = _MD_HEADING.match(line)
        if match:
            headings.append(
                _Heading(level=len(match.group(1)), title=match.group(2), first_line=i, last_line=i)
            )
    return headings


class MarkdownLoader:
    """Markdown with ATX (``#``) headings. A leading H1 is the title, not a section."""

    def parse(self, text: str, *, source: str | None, fallback_title: str) -> ParsedDocument:
        content = normalize_text(text)
        lines = content.split("\n")
        headings = _find_md_headings(lines)
        title = fallback_title
        if headings and headings[0].level == 1:
            title = headings[0].title
            # Demote the remaining headings by one level; the title is not a section.
            rest = [
                _Heading(
                    level=max(1, h.level - 1),
                    title=h.title,
                    first_line=h.first_line,
                    last_line=h.last_line,
                )
                for h in headings[1:]
            ]
            body_start_line = headings[0].last_line + 1
            headings = rest
        else:
            body_start_line = 0
        document = Document(
            id=document_id(content),
            content=content,
            source=source,
            metadata={"title": title, "format": "md"},
        )
        sections = _build_sections(lines, headings, len(content), body_start_line=body_start_line)
        return ParsedDocument(document=document, title=title, sections=sections)


# --------------------------------------------------------------------------- Plain text


class TextLoader:
    """Plain text: the first non-empty line is the title; the whole file is one section."""

    def parse(self, text: str, *, source: str | None, fallback_title: str) -> ParsedDocument:
        content = normalize_text(text)
        first_line = next((line.strip() for line in content.split("\n") if line.strip()), "")
        title = first_line or fallback_title
        document = Document(
            id=document_id(content),
            content=content,
            source=source,
            metadata={"title": title, "format": "txt"},
        )
        sections = [Section(path=(), char_start=0, char_end=len(content))]
        return ParsedDocument(document=document, title=title, sections=sections)


LOADERS: dict[str, Loader] = {
    ".rst": RstLoader(),
    ".md": MarkdownLoader(),
    ".txt": TextLoader(),
}
SUPPORTED_SUFFIXES = frozenset(LOADERS)


def load_file(path: Path, *, source: str | None = None) -> ParsedDocument:
    """Load one file, choosing the loader by suffix. ``source`` defaults to the path."""
    loader = LOADERS.get(path.suffix.lower())
    if loader is None:
        raise ValueError(f"unsupported file type {path.suffix!r}: {path}")
    text = path.read_text(encoding="utf-8")
    return loader.parse(text, source=source or path.as_posix(), fallback_title=path.stem)
