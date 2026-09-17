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
corpus -> ingestion -> retrieval -> generation -> Answer
          (Document,   (RetrievedChunk   (llm provider,
           Chunk)       + stage scores)   prompts)
               |              |               |
               v              v               v
             evals (items, metrics, checks, judges, bootstrap, runner, compare)
               |
               v
      experiments/runs/<ts>_<config>/  (config, results.jsonl, summary.json, report.md)
```

- `config.py`: `Settings` (pydantic-settings, reads `.env`); use `get_settings()`.
- `models.py`: `Document`, `Chunk`, `StageScore`, `RetrievedChunk`, `Citation`, `TokenUsage`,
  `Answer`. Frozen, `extra="forbid"`.
- `ingestion/`: corpus download (pinned commit), loaders (.rst/.md/.txt), structure-aware
  chunking, MinHash dedup, versioned datasets under `data/processed/<dataset_version>/`.
- `retrieval/`: embedder, numpy vector store, BM25, RRF fusion, reranker, `HybridRetriever`,
  index build/load. Configured by `RetrievalConfig` (mode, candidate_k, rerank, final_k).
- `llm/`: provider protocol; the only package allowed to import the `anthropic` SDK. Also the
  fake provider, the disk cache, structured-output parsing and pricing.
- `prompts/`: versioned prompt files (`answer_v1.txt`, `judge_*_v1.txt`, ...). Never edit a
  version in place; add `_v2`.
- `generation/`: grounded answers with citations and abstention.
- `pipelines/`: `RunConfig` YAML loader (retrieval + generation + judge sections).
- `evals/`: eval items (source-level labels), taxonomy, metrics, programmatic checks, LLM
  judges, bootstrap CIs, candidate generation, review session, runner, report, compare.
- `cli/`: the `rag` typer app. Modules there must **not** use
  `from __future__ import annotations` (typer evaluates annotations at runtime).
- `agent/`, `data_quality/`, `api/`, `observability/`: planned (M6-M8).

Full diagram: `docs/architecture.md`. Evaluation methodology: `docs/evaluation.md`.

## Commands

```bash
uv sync                      # install base + dev deps (never install extras by default)
uv sync --extra retrieval    # sentence-transformers + torch; needed for rag index / vector configs
make lint                    # ruff check + ruff format --check
make format                  # ruff format + ruff check --fix
make typecheck               # mypy --strict over src and tests
make test                    # pytest (slow and integration tests are deselected by default)
make check                   # lint + typecheck + test; must pass before every commit
uv run pytest -m slow        # the two model-download tests (run locally, not in CI)
uv run pytest tests/test_models.py -k frozen   # run a single test

uv run rag download-corpus                       # -> data/raw/peps/ + manifest.json
uv run rag ingest [--chunk-size 400] [--overlap 0.15] [--raw-dir DIR]
uv run rag index [--dataset-version V] [--no-vectors]
uv run rag query "question" [--config configs/hybrid_rerank.yaml] [--show-chunks] [--no-generate]
uv run rag eval generate-candidates --n 120
uv run rag eval review eval_sets/candidates/<ts>.jsonl
uv run rag eval run --config configs/<name>.yaml --eval-set v1 [--limit N] [--retrieval-only] [--yes]
uv run rag eval compare <run_a_dir> <run_b_dir>
```

No GNU make on Windows: run the `uv run ...` commands from the Makefile directly.

## Coding standards

- **Type hints everywhere.** mypy runs in strict mode over `src/` and `tests/`. No `Any`
  except at explicit boundaries (e.g. free-form `metadata` dicts). No `# type: ignore`
  without an error code and a reason. Untyped third-party libraries (`rank_bm25`,
  `datasketch`, `sentence_transformers`) are wrapped in one small typed module each.
- **Pydantic models at boundaries.** Anything crossing a module boundary, a file, a
  network call or an LLM call is a pydantic model, not a dict. Reuse `ragplatform.models`;
  add new models next to the code that owns them.
- **No hard-coded secrets.** All configuration comes from `Settings`. Never write an API
  key, token or credential into code, tests, docs or fixtures. Never create a real `.env`.
- **Tests for all pure logic.** Chunkers, fusers, metrics, statistics and parsers get unit
  tests with hand-checkable expected values. Aim for edge cases (empty input, ties, k
  larger than the result list), not just the happy path.
- **Mock LLM calls in unit tests.** Use `ragplatform.llm.FakeProvider` (queued responses or a
  responder function); `mock_responder` returns schema-valid JSON per call purpose. Unit
  tests never touch the network and never need an API key. Tests that download models are
  marked `@pytest.mark.slow`; tests that hit real services `@pytest.mark.integration`. Both
  are deselected by default via `addopts`.
- **Small focused modules.** One responsibility per module, a short module docstring
  saying what it owns. Prefer functions over classes unless there is state to manage.
  Keep files under a few hundred lines.
- **Async for I/O.** LLM calls are `async`. Pure computation is sync.
- **Imports.** ruff's `TC` rules move type-only imports under `TYPE_CHECKING`; pydantic
  models are exempt (`runtime-evaluated-base-classes`). Run `make format` and let ruff
  decide.
- **Style is enforced, not discussed.** ruff (lint + format, line length 100) and mypy
  decide. Run `make format` before `make check`.
- **Docs stay honest.** The README roadmap only ticks a box when the feature is
  implemented, tested and used somewhere. Update the roadmap in the same commit as the
  feature.
- **Commits.** Conventional Commits (`feat:`, `fix:`, `chore:`, `docs:`, `test:`). One
  logical change per commit. Do not push; the owner pushes after review.

## Integrity rules for evaluation

- **Never invent evaluation results, metrics or human labels.** Numbers in docs must come
  from runs that actually executed and are stored under `experiments/runs/`. Quote the run
  id. If a run has not happened, say so.
- **Synthetic questions are candidates until a human reviews them.** Files under
  `eval_sets/candidates/` are never evaluated against. Only `rag eval review` writes to
  `eval_sets/<name>/items.jsonl`, and every item it writes carries
  `created_by = synthetic_reviewed`.
- **`--mock-llm` runs are placeholders.** Their reports carry a "Placeholder run" warning and
  their numbers must never be quoted anywhere.
- **Labels are sources, not chunk ids** (`doc_id` + `section_path`), so labels survive
  re-chunking. Never add chunk ids to eval items.
- **Every run records provenance**: config snapshot, git commit + dirty flag, dataset
  version, eval set version, prompt versions, generator and judge models, LLM provider.
  Do not remove any of it.
- **Prompts are versioned files.** Changing a prompt means a new `_vN` file and a config
  change, never an edit to the old file.
- **Cost before spend.** `rag eval run` prints the estimated calls, tokens and cost and asks
  for confirmation unless `--yes`. Prices live in `configs/pricing.yaml`; keep the
  `checked_on` date current when you touch it.

## Milestone roadmap

| # | Milestone | Scope | Status |
| --- | --- | --- | --- |
| M1 | Foundation | structure, tooling, CI, docs | done |
| M2 | Ingestion | pinned PEP corpus, .rst/.md/.txt loaders, structure-aware chunking, MinHash dedup, versioned datasets | done |
| M3 | Retrieval | bge-small embeddings, numpy vector store, BM25, RRF hybrid search, cross-encoder reranking, YAML configs | done |
| M4 | Generation | provider interface, versioned prompts, grounded answers with validated citations and abstention, disk cache | done |
| M5 | Evaluation harness | eval item schema, taxonomy, candidates + review, retrieval metrics, checks, judges, bootstrap CIs, runner, compare | done (harness); eval set v1 not yet built |
| M6 | Agent | tool-using agent loop (search tool), multi-turn query rewriting, step limits, trajectory logging, pass@k and pass^k | planned |
| M7 | Data quality | failure taxonomy, annotation export, Cohen's kappa, judge-human agreement | planned |
| M8 | Infrastructure | async batch runner with retries, tracing, FastAPI service, Docker | planned |
| M9 | Experiments | chunking, vector-only vs hybrid, reranking ablations with a results report | planned |

When starting a milestone: read the relevant subpackage docstring, add models
first, then pure logic with tests, then the LLM-touching parts with a mocked
provider, then update README roadmap and `docs/architecture.md`.
