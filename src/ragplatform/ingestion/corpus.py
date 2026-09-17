"""Download the PEP corpus from python/peps, pinned to one commit.

Files are fetched from raw.githubusercontent.com at :data:`PEPS_COMMIT`, so the
corpus is byte-for-byte reproducible. A ``manifest.json`` records the repo, the
commit, every file's sha256 and any requested PEP that does not exist at that
commit. The set of PEPs is chosen to cover typing, async, packaging, language
features and process documents.
"""

from __future__ import annotations

import hashlib
import json
import urllib.error
import urllib.request
from collections.abc import Callable
from typing import TYPE_CHECKING

import structlog
from pydantic import BaseModel, ConfigDict, Field

from ragplatform.ingestion.dataset import utc_now_iso

if TYPE_CHECKING:
    from pathlib import Path

log = structlog.get_logger(__name__)

PEPS_REPO = "python/peps"
PEPS_COMMIT = "94a7775f23fd6eb7c527cf8180dab4542c5da622"  # main on 2026-09-11
MANIFEST_FILE = "manifest.json"

# Process / style: 1, 8, 20, 257, 594, 602
# Typing: 483, 484, 526, 544, 557, 563, 585, 586, 589, 593, 604, 612, 646, 647,
#         649, 655, 673, 675, 681, 692, 695, 696, 698, 705, 742, 747, 749
# Async: 492, 525, 530, 654
# Packaging: 427, 440, 508, 517, 518, 621, 723, 735
# Language: 343, 380, 498, 505, 572, 584, 634, 635, 636, 701, 703
DEFAULT_PEPS: tuple[int, ...] = (
    1, 8, 20, 257, 594, 602,
    483, 484, 526, 544, 557, 563, 585, 586, 589, 593, 604, 612, 646, 647,
    649, 655, 673, 675, 681, 692, 695, 696, 698, 705, 742, 747, 749,
    492, 525, 530, 654,
    427, 440, 508, 517, 518, 621, 723, 735,
    343, 380, 498, 505, 572, 584, 634, 635, 636, 701, 703,
)  # fmt: skip

Fetcher = Callable[[str], bytes | None]


class CorpusFile(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    pep: int
    path: str = Field(description="File name inside the corpus directory.")
    sha256: str
    size_bytes: int = Field(ge=0)


class CorpusManifest(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    source_repo: str
    commit_sha: str
    downloaded_at: str
    files: list[CorpusFile]
    missing: list[int] = Field(default_factory=list, description="PEPs absent at the commit.")


def pep_filename(pep: int) -> str:
    return f"pep-{pep:04d}.rst"


def pep_url(pep: int, commit: str = PEPS_COMMIT, repo: str = PEPS_REPO) -> str:
    return f"https://raw.githubusercontent.com/{repo}/{commit}/peps/{pep_filename(pep)}"


def fetch_url(url: str) -> bytes | None:
    """GET a URL; return None on 404. Only https is allowed."""
    if not url.startswith("https://"):
        raise ValueError(f"refusing non-https url: {url}")
    try:
        with urllib.request.urlopen(url, timeout=30) as response:  # noqa: S310 - https enforced above
            return bytes(response.read())
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return None
        raise


def download_peps(
    dest: Path,
    peps: tuple[int, ...] = DEFAULT_PEPS,
    commit: str = PEPS_COMMIT,
    fetch: Fetcher = fetch_url,
) -> CorpusManifest:
    """Download the PEPs into ``dest`` and write ``manifest.json``."""
    dest.mkdir(parents=True, exist_ok=True)
    files: list[CorpusFile] = []
    missing: list[int] = []
    for pep in peps:
        data = fetch(pep_url(pep, commit))
        if data is None:
            missing.append(pep)
            log.warning("pep_missing", pep=pep, commit=commit)
            continue
        path = dest / pep_filename(pep)
        path.write_bytes(data)
        files.append(
            CorpusFile(
                pep=pep,
                path=path.name,
                sha256=hashlib.sha256(data).hexdigest(),
                size_bytes=len(data),
            )
        )
        log.info("pep_downloaded", pep=pep, size_bytes=len(data))
    manifest = CorpusManifest(
        source_repo=PEPS_REPO,
        commit_sha=commit,
        downloaded_at=utc_now_iso(),
        files=files,
        missing=missing,
    )
    (dest / MANIFEST_FILE).write_text(
        json.dumps(manifest.model_dump(), indent=2) + "\n", encoding="utf-8"
    )
    return manifest
