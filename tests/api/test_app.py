"""Service contracts exercised in-process without sockets or paid providers."""

import pytest

pytest.importorskip("fastapi")

from fastapi.testclient import TestClient

from ragplatform.api.app import create_app
from ragplatform.ingestion.chunking import ChunkMetadata
from ragplatform.llm.fake import FakeProvider, mock_responder
from ragplatform.models import Chunk, RetrievedChunk


class Search:
    def retrieve(self, query: str) -> list[RetrievedChunk]:
        return [
            RetrievedChunk(
                chunk=Chunk(
                    id="chunk",
                    document_id="doc",
                    content="Evidence",
                    index=0,
                    metadata=ChunkMetadata(
                        doc_title="Test",
                        section_path="Test",
                        char_start=0,
                        char_end=8,
                        token_count=2,
                    ).to_dict(),
                ),
                rank=1,
                score=1,
                retriever="test",
            )
        ]


def test_retrieval_default_and_paid_boundary() -> None:
    with TestClient(create_app(Search(), dataset_version="test")) as client:
        assert client.get("/health").json()["ready"] is True
        response = client.post("/query", json={"question": "Question"})
        assert response.status_code == 200
        assert response.json()["answer"] is None
        assert len(response.json()["trace_id"]) == 32
        assert client.post("/query", json={"question": "q", "mode": "answer"}).status_code == 403
        assert client.post("/query", json={"question": "q", "mode": "agent"}).status_code == 403
        assert client.post("/query", json={"question": " "}).status_code == 422
        assert client.get("/metrics").json() == {"queries": 3, "completed": 1, "errors": 2}


def test_explicit_fake_provider_and_unconfigured_health() -> None:
    provider = FakeProvider(responder=mock_responder)
    with TestClient(create_app(Search(), provider=provider)) as client:
        response = client.post("/query", json={"question": "q", "mode": "answer"})
        assert response.status_code == 200
        assert response.json()["placeholder"] is True
        assert response.json()["answer"]["citations"][0]["chunk_id"] == "chunk"
        assert provider.calls == 1
    with TestClient(create_app()) as client:
        assert client.get("/health").json()["ready"] is False
        assert client.post("/query", json={"question": "q"}).status_code == 503


def test_errors_do_not_expose_internal_messages() -> None:
    class BrokenSearch:
        def retrieve(self, query: str) -> list[RetrievedChunk]:
            raise RuntimeError("private internal detail")

    with TestClient(create_app(BrokenSearch())) as client:
        response = client.post("/query", json={"question": "q"})
        assert response.status_code == 500
        assert "private" not in response.text
