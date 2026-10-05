"""Capture actual local service responses, without an LLM provider."""

import json
from pathlib import Path

from fastapi.testclient import TestClient

from ragplatform.api.app import create_app
from ragplatform.retrieval.config import RetrievalConfig
from ragplatform.retrieval.index import load_retriever

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    version = "27b46e65f45d"
    search = load_retriever(
        RetrievalConfig(mode="bm25", rerank=False), ROOT / "data/processed" / version
    )
    with TestClient(create_app(search, dataset_version=version)) as client:
        health = client.get("/health")
        query = client.post("/query", json={"question": "PEP 655 Required NotRequired TypedDict"})
        blocked = client.post("/query", json={"question": "test", "mode": "answer"})
        metrics = client.get("/metrics")
        if query.status_code != 200 or blocked.status_code != 403:
            raise RuntimeError("Service smoke check failed")
        data = {
            "verification": "In-process HTTP contract check with real local BM25",
            "llm_calls": 0,
            "health": health.json(),
            "query_status": query.status_code,
            "query": query.json(),
            "generation_status": blocked.status_code,
            "generation": blocked.json(),
            "metrics": metrics.json(),
        }
    target = ROOT / "docs/evidence/infrastructure/service-smoke.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    print(f"Saved {target.name}; retrieval 200; generation 403; no provider constructed")


if __name__ == "__main__":
    main()
