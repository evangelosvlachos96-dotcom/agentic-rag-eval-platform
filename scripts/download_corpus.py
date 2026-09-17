"""Download the pinned PEP corpus. Equivalent to ``rag download-corpus``.

Usage: ``uv run python scripts/download_corpus.py [--dest DIR]``
"""

from __future__ import annotations

import typer

from ragplatform.cli.ingest_cmds import download_corpus

if __name__ == "__main__":
    typer.run(download_corpus)
