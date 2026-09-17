"""Slow tests: they download the real sentence-transformers models.

Run explicitly with ``uv run pytest -m slow``. Excluded from CI.
"""

from __future__ import annotations

import numpy as np
import pytest

from ragplatform.config import Settings
from ragplatform.models import Chunk

pytestmark = pytest.mark.slow


def test_sentence_transformer_embedder_normalizes_and_batches() -> None:
    from ragplatform.retrieval.embedder import SentenceTransformerEmbedder

    embedder = SentenceTransformerEmbedder(Settings(_env_file=None).embedding_model, batch_size=2)
    vectors = embedder.embed_documents(["type hints", "async generators", "wheel packaging"])
    assert vectors.shape == (3, 384)
    assert vectors.dtype == np.float32
    assert np.allclose(np.linalg.norm(vectors, axis=1), 1.0, atol=1e-5)
    query = embedder.embed_query("what are type hints?")
    scores = vectors @ query
    assert int(np.argmax(scores)) == 0


def test_cross_encoder_reranker_prefers_relevant_passage() -> None:
    from ragplatform.retrieval.reranker import CrossEncoderReranker

    reranker = CrossEncoderReranker(Settings(_env_file=None).reranker_model)
    chunks = [
        Chunk(id="cake", document_id="d", content="Preheat the oven and mix the flour.", index=0),
        Chunk(
            id="typing",
            document_id="d",
            content="PEP 484 introduces type hints for function annotations.",
            index=1,
        ),
    ]
    ranked = reranker.rerank("Which PEP introduced type hints?", chunks)
    assert [i for i, _ in ranked] == ["typing", "cake"]
    assert ranked[0][1] > ranked[1][1]
