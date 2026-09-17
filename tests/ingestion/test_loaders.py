"""Tests for ragplatform.ingestion.loaders."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from ragplatform.ingestion.loaders import (
    MarkdownLoader,
    RstLoader,
    TextLoader,
    document_id,
    load_file,
    normalize_text,
)

if TYPE_CHECKING:
    from pathlib import Path


def test_normalize_unifies_line_endings_and_trailing_whitespace() -> None:
    assert normalize_text("a  \r\nb\t\r\n\r\n") == "a\nb"


def test_document_id_is_stable_under_normalization() -> None:
    assert document_id("hello\r\nworld  ") == document_id("hello\nworld")
    assert document_id("hello") != document_id("hello!")
    assert len(document_id("x")) == 16


def test_rst_loader_extracts_title_headers_and_nested_sections(fixture_corpus_dir: Path) -> None:
    parsed = load_file(fixture_corpus_dir / "widget-protocol.rst")
    assert parsed.title == "Widget Transfer Protocol"
    assert parsed.document.metadata["headers"]["Status"] == "Final"
    paths = [s.path for s in parsed.sections]
    assert paths == [
        (),
        ("Abstract",),
        ("Specification",),
        ("Specification", "Handshake"),
        ("Specification", "Framing"),
        ("Specification", "Error codes"),
        ("Rationale",),
    ]
    framing = parsed.sections[4]
    text = parsed.section_text(framing)
    assert text.strip().startswith("Every frame starts")
    assert "ZX-9000-ALPHA" in text
    assert "Error codes" not in text  # heading lines are never part of a body


def test_rst_overlined_title_and_level_order() -> None:
    text = "=====\nTitle\n=====\n\nIntro.\n\nPart\n----\n\nBody.\n\nSub\n~~~\n\nDeep.\n"
    parsed = RstLoader().parse(text, source=None, fallback_title="x")
    assert parsed.title == "Title"
    assert [s.path for s in parsed.sections] == [
        ("Title",),
        ("Title", "Part"),
        ("Title", "Part", "Sub"),
    ]


def test_markdown_loader_uses_h1_as_title_and_skips_fenced_headings(
    fixture_corpus_dir: Path,
) -> None:
    parsed = load_file(fixture_corpus_dir / "gadget-guide.md")
    assert parsed.title == "Gadget Assembly Guide"
    assert [s.path for s in parsed.sections] == [
        (),
        ("Parts list",),
        ("Assembly",),
        ("Assembly", "Mounting the hinges"),
        ("Assembly", "Fitting the controller"),
        ("Rationale",),
    ]
    fenced = "# T\n\n```\n# not a heading\n```\n\n## Real\n\nbody\n"
    fenced_doc = MarkdownLoader().parse(fenced, source=None, fallback_title="f")
    assert [s.path for s in fenced_doc.sections] == [(), ("Real",)]


def test_text_loader_single_section(fixture_corpus_dir: Path) -> None:
    parsed = load_file(fixture_corpus_dir / "release-notes.txt")
    assert parsed.title == "Release notes for the fixture corpus"
    assert len(parsed.sections) == 1
    assert parsed.section_text(parsed.sections[0]) == parsed.document.content


def test_text_loader_falls_back_to_name_for_blank_document() -> None:
    parsed = TextLoader().parse("\n\n x \n", source=None, fallback_title="notes")
    assert parsed.title == "x"


def test_unsupported_suffix_raises(tmp_path: Path) -> None:
    path = tmp_path / "doc.pdf"
    path.write_bytes(b"%PDF")
    with pytest.raises(ValueError, match="unsupported"):
        load_file(path)
