# scripts/

Thin wrappers around library code so that all logic stays tested.

- `download_corpus.py`: same as `rag download-corpus`
  (`uv run python scripts/download_corpus.py [--dest DIR]`).

- `run_live_validation.py`: budgeted paid suite; without `--execute`, prints the plan only.
- `build_results_page.py`: generates `docs/index.html` from saved evidence, with no API calls.
- `render_results_page.cjs`: Playwright desktop/mobile screenshots and local link/layout checks.

Other commands are exposed through the `rag` CLI (`uv run rag --help`).
