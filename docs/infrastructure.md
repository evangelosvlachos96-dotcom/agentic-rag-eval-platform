# Local service and batch infrastructure

Install optional API dependencies before type checking or running the service:

```powershell
uv sync --locked --extra api
$env:RAG_DATASET_DIR = "data/processed/27b46e65f45d"
uv run --extra api uvicorn ragplatform.api.app:local_app --factory --host 127.0.0.1 --port 8000
```

`GET /health` reports readiness and whether a provider was explicitly injected.
`GET /metrics` returns in-process query, completion and error counters.
`POST /query` accepts `{"question":"What does PEP 655 specify?","mode":"retrieve"}`.
It returns passages, source metadata, dataset version and a correlation ID. The
local factory always uses BM25 and disables generation. An environment API key
cannot enable it. Answer and agent modes return HTTP 403 without an injected
provider. Tests exercise those modes using FakeProvider only.

The service bounds input length, concurrency and request time. Query execution
runs blocking retrieval in a thread; cancellation does not kill a running thread.
This is a local showcase service, not a public multi-tenant deployment: it has no
authentication, distributed rate limiting or persistent metrics. Bind to loopback.
Timings and correlation IDs are logged without question text or retrieved content.
Agent trajectories intentionally include content and should be handled as data.

`pipelines.run_batch` preserves input order with a bounded worker pool. The default
is one attempt. Only `RetryableError` is retried with bounded exponential backoff;
permanent failures and timeouts are recorded without retrying. Cancellation
propagates. Callers must decide whether retrying external side effects is safe.

## Docker

```powershell
docker build -t agentic-rag-eval-platform:local .
docker run --rm -p 127.0.0.1:8000:8000 --mount "type=bind,source=ABSOLUTE_DATASET_PATH,target=/data/dataset,readonly" agentic-rag-eval-platform:local
```

The image installs locked dependencies, runs as a non-root user, and receives the
prebuilt BM25 dataset through a read-only mount. Secrets, local virtual environments,
and experiment outputs are excluded from the build context. No model keys are
passed to the container.

The in-process smoke artifact is `docs/evidence/infrastructure/service-smoke.json`.
It verifies real BM25 retrieval (HTTP 200), generation disabled (HTTP 403), readiness
and counters. Container validation is recorded separately after the actual build/run.

Container smoke checks passed with eight retrieved passages, HTTP 403 for generation, non-root UID 10001, external networking disabled and a read-only filesystem. See container-smoke.json and scripts/check_container.ps1.
