"""Tests for ragplatform.ingestion.corpus (network replaced by a fake fetcher)."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

import pytest

from ragplatform.ingestion.corpus import (
    DEFAULT_PEPS,
    PEPS_COMMIT,
    download_peps,
    fetch_url,
    pep_url,
)

if TYPE_CHECKING:
    from pathlib import Path


def test_pep_url_is_pinned_to_commit() -> None:
    assert pep_url(484) == (
        f"https://raw.githubusercontent.com/python/peps/{PEPS_COMMIT}/peps/pep-0484.rst"
    )


def test_default_pep_list_is_varied_and_unique() -> None:
    assert len(DEFAULT_PEPS) == len(set(DEFAULT_PEPS))
    assert 50 <= len(DEFAULT_PEPS) <= 60
    assert {8, 484, 492, 517, 572, 634} <= set(DEFAULT_PEPS)


def test_download_writes_files_and_manifest_and_reports_missing(tmp_path: Path) -> None:
    def fake_fetch(url: str) -> bytes | None:
        if url.endswith("pep-0008.rst"):
            return b"PEP: 8\nTitle: Style Guide\n"
        return None

    manifest = download_peps(tmp_path, peps=(8, 9999), fetch=fake_fetch)
    assert [f.pep for f in manifest.files] == [8]
    assert manifest.missing == [9999]
    assert manifest.commit_sha == PEPS_COMMIT
    assert (tmp_path / "pep-0008.rst").read_bytes() == b"PEP: 8\nTitle: Style Guide\n"
    on_disk = json.loads((tmp_path / "manifest.json").read_text(encoding="utf-8"))
    assert on_disk["files"][0]["sha256"] == manifest.files[0].sha256
    assert on_disk["source_repo"] == "python/peps"


def test_fetch_url_rejects_plain_http() -> None:
    with pytest.raises(ValueError, match="https"):
        fetch_url("http://example.com/x")
