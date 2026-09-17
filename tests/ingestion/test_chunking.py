"""Tests for ragplatform.ingestion.chunking."""

from __future__ import annotations

import itertools
from typing import TYPE_CHECKING

from ragplatform.ingestion.chunking import (
    ChunkingConfig,
    ChunkMetadata,
    chunk_document,
    index_text,
)
from ragplatform.ingestion.loaders import MarkdownLoader, load_file
from ragplatform.ingestion.tokens import ApproxTokenCounter

if TYPE_CHECKING:
    from pathlib import Path


def test_approx_token_counter() -> None:
    counter = ApproxTokenCounter()
    assert counter.count("") == 0
    assert counter.count("abc") == 1
    assert counter.count("a" * 9) == 3


def test_small_sections_become_one_chunk_each(fixture_corpus_dir: Path) -> None:
    parsed = load_file(fixture_corpus_dir / "widget-protocol.rst")
    chunks = chunk_document(parsed, ChunkingConfig(max_tokens=400))
    paths = [ChunkMetadata.from_chunk(c).section_path for c in chunks]
    assert paths == [
        "",
        "Abstract",
        "Specification > Handshake",
        "Specification > Framing",
        "Specification > Error codes",
        "Rationale",
    ]
    # "Specification" itself has no body text (only sub-sections), so no chunk.
    assert [c.index for c in chunks] == list(range(len(chunks)))
    assert chunks[0].id == f"{parsed.document.id}-0000"


def test_offsets_map_back_to_source_text(fixture_corpus_dir: Path) -> None:
    for name in ("widget-protocol.rst", "gadget-guide.md", "release-notes.txt"):
        parsed = load_file(fixture_corpus_dir / name)
        for chunk in chunk_document(parsed, ChunkingConfig(max_tokens=40, overlap_ratio=0.2)):
            meta = ChunkMetadata.from_chunk(chunk)
            assert parsed.document.content[meta.char_start : meta.char_end] == chunk.content
            assert chunk.content == chunk.content.strip()


def test_token_budget_is_respected_and_paragraphs_preferred() -> None:
    paragraphs = [f"Paragraph {i} has exactly this much text in it." for i in range(6)]
    text = "# Doc\n\n## Body\n\n" + "\n\n".join(paragraphs) + "\n"
    parsed = MarkdownLoader().parse(text, source=None, fallback_title="d")
    counter = ApproxTokenCounter()
    config = ChunkingConfig(max_tokens=30, overlap_ratio=0.0)
    chunks = chunk_document(parsed, config, counter)
    assert len(chunks) > 1
    for chunk in chunks:
        assert ChunkMetadata.from_chunk(chunk).token_count <= 30
        # Breaks happen at paragraph boundaries: every chunk is whole paragraphs.
        for piece in chunk.content.split("\n\n"):
            assert piece in paragraphs
    # No overlap: the chunks tile the section exactly.
    assert "\n\n".join(c.content for c in chunks) == "\n\n".join(paragraphs)


def test_overlap_repeats_trailing_units() -> None:
    sentences = [f"Sentence number {i} is here." for i in range(8)]
    text = "# Doc\n\n" + " ".join(sentences) + "\n"  # one long paragraph -> sentence split
    parsed = MarkdownLoader().parse(text, source=None, fallback_title="d")
    config = ChunkingConfig(max_tokens=20, overlap_ratio=0.5)  # 10 overlap tokens
    chunks = chunk_document(parsed, config)
    assert len(chunks) >= 3
    for previous, current in itertools.pairwise(chunks):
        # The next chunk starts with the last sentence of the previous one.
        last_sentence = previous.content.split(". ")[-1].rstrip(".")
        assert current.content.startswith(last_sentence)
        assert (
            ChunkMetadata.from_chunk(current).char_start
            > ChunkMetadata.from_chunk(previous).char_start
        )


def test_overlong_sentence_falls_back_to_word_groups() -> None:
    words = " ".join(f"w{i}" for i in range(60))  # no sentence punctuation at all
    parsed = MarkdownLoader().parse(f"# D\n\n{words}\n", source=None, fallback_title="d")
    chunks = chunk_document(parsed, ChunkingConfig(max_tokens=10, overlap_ratio=0.0))
    assert len(chunks) > 1
    assert " ".join(c.content for c in chunks) == words
    for chunk in chunks:
        assert ChunkMetadata.from_chunk(chunk).token_count <= 10


def test_contextual_header_prefixes_index_text_only(fixture_corpus_dir: Path) -> None:
    parsed = load_file(fixture_corpus_dir / "widget-protocol.rst")
    chunks = chunk_document(parsed, ChunkingConfig(contextual_header=True))
    framing = next(c for c in chunks if "ZX-9000-ALPHA" in c.content)
    assert index_text(framing).startswith("Widget Transfer Protocol > Specification > Framing\n\n")
    assert framing.content.startswith("Every frame starts")

    plain = chunk_document(parsed, ChunkingConfig(contextual_header=False))
    assert all(index_text(c) == c.content for c in plain)
    preamble = chunks[0]
    assert ChunkMetadata.from_chunk(preamble).context_header == "Widget Transfer Protocol"


def test_empty_sections_produce_no_chunks() -> None:
    parsed = MarkdownLoader().parse(
        "# T\n\n## Empty\n\n\n## Full\n\ntext\n", source=None, fallback_title="t"
    )
    chunks = chunk_document(parsed)
    assert [ChunkMetadata.from_chunk(c).section_path for c in chunks] == ["Full"]
