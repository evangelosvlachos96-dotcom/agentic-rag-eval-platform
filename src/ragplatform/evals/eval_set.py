"""Eval sets on disk: ``eval_sets/<name>/items.jsonl`` plus ``manifest.json``.

The eval set version is the first 12 hex chars of the sha256 of ``items.jsonl``,
so every run records exactly which labels it was scored against.
"""

from __future__ import annotations

import hashlib
from typing import TYPE_CHECKING

from pydantic import BaseModel, ConfigDict, Field

from ragplatform.evals.models import EvalItem
from ragplatform.ingestion.dataset import utc_now_iso

if TYPE_CHECKING:
    from collections.abc import Iterable
    from pathlib import Path

ITEMS_FILE = "items.jsonl"
MANIFEST_FILE = "manifest.json"


class EvalSetManifest(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    name: str
    version: str = Field(description="sha256[:12] of items.jsonl")
    n_items: int = Field(ge=0)
    n_unanswerable: int = Field(ge=0)
    updated_at: str


def read_items(path: Path) -> list[EvalItem]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8") as handle:
        items = [EvalItem.model_validate_json(line) for line in handle if line.strip()]
    ids = [item.id for item in items]
    if len(ids) != len(set(ids)):
        raise ValueError(f"duplicate item ids in {path}")
    return items


def write_items(path: Path, items: Iterable[EvalItem]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for item in items:
            handle.write(item.model_dump_json() + "\n")


def append_item(path: Path, item: EvalItem) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(item.model_dump_json() + "\n")


def eval_set_version(items_path: Path) -> str:
    return hashlib.sha256(items_path.read_bytes()).hexdigest()[:12]


def write_manifest(directory: Path, name: str) -> EvalSetManifest:
    items = read_items(directory / ITEMS_FILE)
    manifest = EvalSetManifest(
        name=name,
        version=eval_set_version(directory / ITEMS_FILE),
        n_items=len(items),
        n_unanswerable=sum(1 for i in items if not i.answerable),
        updated_at=utc_now_iso(),
    )
    (directory / MANIFEST_FILE).write_text(manifest.model_dump_json(indent=2), encoding="utf-8")
    return manifest


def load_eval_set(eval_sets_dir: Path, name: str) -> tuple[list[EvalItem], str]:
    """Items and version of ``eval_sets/<name>``; raises if the set is missing or empty."""
    items_path = eval_sets_dir / name / ITEMS_FILE
    if not items_path.exists():
        raise FileNotFoundError(f"eval set {name!r} not found at {items_path}")
    items = read_items(items_path)
    if not items:
        raise ValueError(f"eval set {name!r} has no items")
    return items, eval_set_version(items_path)
