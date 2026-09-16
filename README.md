# agentic-rag-eval-platform

[![CI](https://github.com/evangelosvlachos/agentic-rag-eval-platform/actions/workflows/ci.yml/badge.svg)](https://github.com/evangelosvlachos/agentic-rag-eval-platform/actions/workflows/ci.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

A production-style agentic RAG system with hybrid retrieval, reranking, a
tool-using agent, and a rigorous evaluation and data-quality layer. Most RAG
demos stop at "it answered the question"; this project exists to show the other
half of the job: measuring retrieval and generation separately, calibrating LLM
judges against human labels, quantifying agent reliability with pass^k, and
running ablations whose results you can actually trust. It is built as a
portfolio piece for applied-AI / forward-deployed engineering work, with the
same tooling discipline you would want in a real deployment.

> **Status:** Milestone 1 (foundation) is complete. Nothing below the
> foundation is implemented yet. The roadmap is honest about that.

## Planned architecture

```mermaid
flowchart LR
    subgraph Ingestion["Ingestion (M2)"]
        RAW[Raw documents] --> CHUNK[Structure-aware chunking] --> META[Metadata + dedup]
    end

    subgraph Index["Indexing (M3)"]
        META --> EMB[Embedder] --> VS[(Vector store)]
        META --> BM25[(BM25 index)]
    end

    subgraph Retrieval["Retrieval (M3)"]
        Q[Query] --> VSEARCH[Vector search] & LSEARCH[Lexical search]
        VS --> VSEARCH
        BM25 --> LSEARCH
        VSEARCH & LSEARCH --> RRF[RRF fusion] --> RERANK[Reranker]
    end

    subgraph Agent["Agent (M6)"]
        USER[User question] --> LOOP[Tool-using loop]
        LOOP -- search tool --> Q
        RERANK --> LOOP
        LOOP --> GEN["Grounded generation (M4)<br/>citations + abstention"]
    end

    GEN --> ANSWER[Answer + citations]
    LOOP -.-> LLM[LLM provider<br/>Anthropic]
    GEN -.-> LLM

    subgraph Evaluation["Evaluation + data quality (M5, M7)"]
        SETS[(Versioned eval sets)] --> RM[Retrieval metrics] & GM[Generation checks]
        GM --> JUDGE[LLM judge] --> KAPPA[Judge vs human agreement]
        LOOP --> TRAJ[Trajectories] --> PASSK[pass@k / pass^k]
        RM & JUDGE & PASSK --> CI[Bootstrap CIs]
    end

    RERANK -.-> RM
    ANSWER -.-> GM
```

Full diagram and design notes: [docs/architecture.md](docs/architecture.md).

## Roadmap

### Milestone 1: Foundation
- [x] `src` layout with `ragplatform` package and documented subpackages
- [x] `uv` project with light base install and optional `retrieval` / `eval` / `api` extras
- [x] Settings via pydantic-settings loading from `.env`
- [x] Core pydantic models: `Document`, `Chunk`, `RetrievedChunk`, `Citation`, `Answer`
- [x] ruff, strict mypy, pytest, pre-commit
- [x] Makefile (`install`, `lint`, `format`, `typecheck`, `test`, `check`)
- [x] GitHub Actions CI (lint, typecheck, tests on 3.11 and 3.12)
- [x] README, CLAUDE.md, architecture doc

### Milestone 2: Ingestion
- [ ] Document loading (text, Markdown, HTML, PDF)
- [ ] Structure-aware chunking with overlap and token budgets
- [ ] Metadata extraction and propagation
- [ ] Near-duplicate detection

### Milestone 3: Retrieval
- [ ] Pluggable embedder with local sentence-transformers default
- [ ] Vector store abstraction
- [ ] BM25 lexical retrieval
- [ ] Hybrid search with Reciprocal Rank Fusion
- [ ] Cross-encoder reranking

### Milestone 4: Generation
- [ ] LLM provider interface with async Anthropic client and retries
- [ ] Grounded answers with citations
- [ ] Abstention when the context does not support an answer

### Milestone 5: Evaluation harness
- [ ] Versioned test set
- [ ] Retrieval metrics: recall@k, MRR, nDCG
- [ ] Programmatic faithfulness and citation checks
- [ ] LLM judge with bias mitigation
- [ ] Bootstrap confidence intervals

### Milestone 6: Agent
- [ ] Tool-using agent loop with a search tool
- [ ] Multi-turn query rewriting
- [ ] Step limits
- [ ] Trajectory logging
- [ ] pass@k and pass^k

### Milestone 7: Data quality
- [ ] Failure taxonomy
- [ ] Annotation export
- [ ] Cohen's kappa
- [ ] Judge-human agreement

### Milestone 8: Infrastructure
- [ ] Async batch runner with retries
- [ ] Tracing
- [ ] FastAPI service
- [ ] Docker

### Milestone 9: Experiments
- [ ] Chunking ablation
- [ ] Vector-only vs hybrid retrieval
- [ ] Reranking ablation
- [ ] Results report

## Quickstart

Requires Python 3.11+ and [uv](https://docs.astral.sh/uv/).

```bash
git clone https://github.com/evangelosvlachos/agentic-rag-eval-platform.git
cd agentic-rag-eval-platform

uv sync                     # base + dev dependencies, creates .venv
cp .env.example .env        # then set ANTHROPIC_API_KEY (not needed for make check)
make check                  # lint + typecheck + tests
```

Optional extras, installed only when you need them:

```bash
uv sync --extra retrieval   # sentence-transformers, rank-bm25, numpy
uv sync --extra eval        # numpy, scipy
uv sync --extra api         # fastapi, uvicorn
uv sync --all-extras
```

On Windows without GNU make, run the commands from the `Makefile` directly, e.g.
`uv run ruff check .`, `uv run mypy`, `uv run pytest`.

## Project structure

```
agentic-rag-eval-platform/
├── src/ragplatform/
│   ├── config.py          # settings via pydantic-settings
│   ├── models.py          # Document, Chunk, RetrievedChunk, Citation, Answer
│   ├── ingestion/         # parsing, chunking, metadata, dedup            (M2)
│   ├── retrieval/         # embeddings, BM25, vector store, RRF, reranking (M3)
│   ├── llm/               # provider interface, async client with retries  (M4)
│   ├── evals/             # metrics, LLM judge, pass@k / pass^k, CIs      (M5, M6)
│   ├── agent/             # tool-using loop, tools, context management     (M6)
│   ├── data_quality/      # failure taxonomy, labeling, kappa, dedup       (M7)
│   ├── pipelines/         # dataset versioning, experiment runs            (M8, M9)
│   ├── api/               # FastAPI app                                    (M8)
│   └── observability/     # structured logging and tracing                 (M8)
├── tests/                 # mirrors the package; unit tests mock all LLM calls
├── data/                  # raw/ and processed/ (gitignored contents)
├── eval_sets/             # versioned test sets, tracked in git
├── experiments/           # run outputs (gitignored except README)
├── docs/                  # architecture.md and future reports
├── scripts/               # thin CLI wrappers around library code
├── .github/workflows/     # CI
├── pyproject.toml         # deps, extras, ruff / mypy / pytest config
├── Makefile
└── CLAUDE.md              # conventions for AI-assisted sessions
```

## Evaluation philosophy

**Retrieval and generation are evaluated separately.** A bad answer can come
from not finding the right passage or from misusing a passage that was found.
Retrieval gets recall@k, MRR and nDCG against labeled relevant chunks;
generation gets faithfulness and citation checks against the retrieved context.
Blending them into one score hides which component to fix.

**Programmatic checks come before LLM judges.** Whatever can be verified with
code is verified with code: does every citation point at a retrieved chunk, is
the quoted span actually in the chunk, did the system abstain when the eval set
says it should. LLM judges are reserved for the residual questions code cannot
answer, such as whether an answer is complete.

**Judges are calibrated against human labels.** An LLM judge is a model with its
own biases (position, verbosity, self-preference). Before its scores are trusted
we measure its agreement with human annotations using Cohen's kappa, and apply
mitigations such as swapping candidate order and scoring against a rubric rather
than a free-form opinion.

**Reliability is measured with pass^k, not just pass@k.** pass@k asks whether at
least one of k attempts succeeds, which is the right question for a human in the
loop picking the best. pass^k asks whether all k attempts succeed, which is the
right question for an autonomous agent that must be right every time. Both are
reported, with bootstrap confidence intervals so that small differences between
configurations are not mistaken for improvements.

## License

MIT. See [LICENSE](LICENSE).
