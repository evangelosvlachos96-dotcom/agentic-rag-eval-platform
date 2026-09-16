# CLAUDE.md

Conventions for working in this repository. Read before making changes.

## What this project is

A production-style agentic RAG system with hybrid retrieval, reranking, a
tool-using agent, and a rigorous evaluation and data-quality layer. It is a
portfolio project for applied-AI / forward-deployed engineering, so code
quality, honest documentation and measurable results matter as much as
features. Never claim in docs that something works unless it is built and
tested.

## Architecture overview

Package `ragplatform` under `src/`. Data flows left to right; every arrow is a
pydantic model from `ragplatform.models`.

```
ingestion  ->  retrieval  ->  agent / generation  ->  Answer
 (Document,     (RetrievedChunk)   (llm provider)
  Chunk)
                     |                  |
                     v                  v
             evals + data_quality  <-  pipelines (datasets, experiment runs)
                     |
                     v
          observability (structlog, tracing), api (FastAPI)
```

- `config.py`: `Settings` (pydantic-settings, reads `.env`); use `get_settings()`.
- `models.py`: `Document`, `Chunk`, `RetrievedChunk`, `Citation`, `Answer`. Frozen, `extra="forbid"`.
- `ingestion/`: loaders, structure-aware chunking, metadata, dedup.
- `retrieval/`: embedder interface, vector store, BM25, RRF fusion, reranking.
- `llm/`: provider protocol; the only package allowed to import the `anthropic` SDK.
- `agent/`: tool-using loop, search tool, query rewriting, step limits, trajectories.
- `evals/`: recall@k, MRR, nDCG, faithfulness, LLM judge, pass@k / pass^k, bootstrap CIs.
- `data_quality/`: failure taxonomy, annotation export, Cohen's kappa, judge-human agreement.
- `pipelines/`: dataset versioning, experiment runner, async batch runner.
- `api/`: FastAPI service (optional `api` extra).
- `observability/`: structlog config and tracing.

Full diagram: `docs/architecture.md`.

## Commands

```bash
uv sync                      # install base + dev deps (never install extras by default)
uv sync --extra retrieval    # only when working on embeddings / reranking
make lint                    # ruff check + ruff format --check
make format                  # ruff format + ruff check --fix
make typecheck               # mypy --strict over src and tests
make test                    # pytest
make check                   # lint + typecheck + test; must pass before every commit
uv run pytest tests/test_models.py -k frozen   # run a single test
```

No GNU make on Windows: run the `uv run ...` commands from the Makefile directly.

## Coding standards

- **Type hints everywhere.** mypy runs in strict mode over `src/` and `tests/`. No `Any`
  except at explicit boundaries (e.g. free-form `metadata` dicts). No `# type: ignore`
  without an error code and a reason.
- **Pydantic models at boundaries.** Anything crossing a module boundary, a file, a
  network call or an LLM call is a pydantic model, not a dict. Reuse `ragplatform.models`;
  add new models next to the code that owns them.
- **No hard-coded secrets.** All configuration comes from `Settings`. Never write an API
  key, token or credential into code, tests, docs or fixtures. Never create a real `.env`.
- **Tests for all pure logic.** Chunkers, fusers, metrics, statistics and parsers get unit
  tests with hand-checkable expected values. Aim for edge cases (empty input, ties, k
  larger than the result list), not just the happy path.
- **Mock LLM calls in unit tests.** Unit tests never touch the network and never need an
  API key. Use the fake provider in `ragplatform.llm` (once it exists) or monkeypatch.
  Tests that hit real services are marked `@pytest.mark.integration` and are skipped in CI.
- **Small focused modules.** One responsibility per module, a short module docstring
  saying what it owns. Prefer functions over classes unless there is state to manage.
  Keep files under a few hundred lines.
- **Async for I/O.** LLM calls, HTTP and batch runners are `async`. Pure computation is sync.
- **Style is enforced, not discussed.** ruff (lint + format, line length 100) and mypy
  decide. Run `make format` before `make check`.
- **Docs stay honest.** The README roadmap only ticks a box when the feature is
  implemented, tested and used somewhere. Update the roadmap in the same commit as the
  feature.
- **Commits.** Conventional Commits (`feat:`, `fix:`, `chore:`, `docs:`, `test:`). One
  logical change per commit. Do not push; the owner pushes after review.

## Milestone roadmap

| # | Milestone | Scope | Status |
| --- | --- | --- | --- |
| M1 | Foundation | structure, tooling, CI, docs | done |
| M2 | Ingestion | document loading, structure-aware chunking, metadata, dedup | planned |
| M3 | Retrieval | embeddings, vector store, BM25, RRF hybrid search, reranking | planned |
| M4 | Generation | grounded answers with citations and abstention | planned |
| M5 | Evaluation harness | test set, recall@k, MRR, nDCG, faithfulness, LLM judge with bias mitigation, bootstrap confidence intervals | planned |
| M6 | Agent | tool-using agent loop (search tool), multi-turn query rewriting, step limits, trajectory logging, pass@k and pass^k | planned |
| M7 | Data quality | failure taxonomy, annotation export, Cohen's kappa, judge-human agreement | planned |
| M8 | Infrastructure | async batch runner with retries, tracing, FastAPI service, Docker | planned |
| M9 | Experiments | chunking, vector-only vs hybrid, reranking ablations with a results report | planned |

When starting a milestone: read the relevant subpackage docstring, add models
first, then pure logic with tests, then the LLM-touching parts with a mocked
provider, then update README roadmap and `docs/architecture.md`.
