"""Tests for the EvalItem schema and eval set files, including the shipped fixture set."""

from __future__ import annotations

from pathlib import Path

import pytest
from pydantic import ValidationError

from ragplatform.evals.eval_set import (
    append_item,
    eval_set_version,
    load_eval_set,
    read_items,
    write_items,
    write_manifest,
)
from ragplatform.evals.models import EvalItem, SourceRef

EVAL_SETS_DIR = Path(__file__).resolve().parents[2] / "eval_sets"


def _item(i: int) -> EvalItem:
    return EvalItem(
        id=f"i{i}",
        question="q?",
        reference_answer="a",
        relevant_sources=[SourceRef(doc_id="d", section_path="S")],
        category="lookup",
        created_by="human",
    )


def test_item_validation_rules() -> None:
    with pytest.raises(ValidationError, match="at least one relevant source"):
        EvalItem(id="x", question="q", reference_answer="a", category="lookup", created_by="human")
    with pytest.raises(ValidationError, match="unanswerable"):
        EvalItem(
            id="x",
            question="q",
            reference_answer="a",
            category="lookup",
            answerable=False,
            created_by="human",
        )
    with pytest.raises(ValidationError, match="unanswerable"):
        EvalItem(
            id="x",
            question="q",
            reference_answer="a",
            relevant_sources=[SourceRef(doc_id="d")],
            category="unanswerable",
            answerable=True,
            created_by="human",
        )
    ok = EvalItem(
        id="x",
        question="q",
        reference_answer="n/a",
        category="unanswerable",
        answerable=False,
        created_by="synthetic_reviewed",
    )
    assert ok.relevant_sources == []


def test_write_append_read_and_version(tmp_path: Path) -> None:
    directory = tmp_path / "v1"
    path = directory / "items.jsonl"
    write_items(path, [_item(1), _item(2)])
    append_item(path, _item(3))
    assert [i.id for i in read_items(path)] == ["i1", "i2", "i3"]
    v1 = eval_set_version(path)
    append_item(path, _item(4))
    assert eval_set_version(path) != v1
    manifest = write_manifest(directory, "v1")
    assert manifest.n_items == 4
    assert manifest.version == eval_set_version(path)
    items, version = load_eval_set(tmp_path, "v1")
    assert len(items) == 4
    assert version == manifest.version


def test_duplicate_ids_and_missing_sets_are_rejected(tmp_path: Path) -> None:
    path = tmp_path / "dup" / "items.jsonl"
    write_items(path, [_item(1), _item(1)])
    with pytest.raises(ValueError, match="duplicate"):
        read_items(path)
    with pytest.raises(FileNotFoundError):
        load_eval_set(tmp_path, "nope")
    write_items(tmp_path / "empty" / "items.jsonl", [])
    with pytest.raises(ValueError, match="no items"):
        load_eval_set(tmp_path, "empty")


def test_shipped_fixture_eval_set_is_valid() -> None:
    items, version = load_eval_set(EVAL_SETS_DIR, "fixture")
    assert len(items) == 5
    assert sum(1 for i in items if not i.answerable) == 1
    assert all(i.created_by == "human" for i in items)
    assert len(version) == 12
