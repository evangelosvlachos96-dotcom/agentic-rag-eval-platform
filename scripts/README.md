# scripts/

Thin wrappers around library code so that all logic stays tested.

- `download_corpus.py`: same as `rag download-corpus`
  (`uv run python scripts/download_corpus.py [--dest DIR]`).

Everything else is exposed through the `rag` CLI (`uv run rag --help`).
