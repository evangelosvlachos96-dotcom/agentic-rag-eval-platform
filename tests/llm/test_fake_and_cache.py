"""Tests for the fake provider and the disk cache."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from ragplatform.llm.cache import CachedProvider, cache_key
from ragplatform.llm.fake import FakeProvider, mock_responder
from ragplatform.llm.provider import ChatMessage, CompletionRequest, LLMError

if TYPE_CHECKING:
    from pathlib import Path


def _request(user: str = "hi", purpose: str = "generic", model: str = "m") -> CompletionRequest:
    return CompletionRequest.single_turn(model=model, system="sys", user=user, purpose=purpose)


async def test_fake_provider_replays_queue_and_records_requests() -> None:
    provider = FakeProvider(responses=["one", "two"])
    assert (await provider.complete(_request("a"))).text == "one"
    assert (await provider.complete(_request("b"))).text == "two"
    assert [r.messages[0].content for r in provider.requests] == ["a", "b"]
    assert provider.calls == 2
    with pytest.raises(LLMError, match="no responses left"):
        await provider.complete(_request("c"))


def test_fake_provider_requires_exactly_one_source() -> None:
    with pytest.raises(ValueError, match="exactly one"):
        FakeProvider()
    with pytest.raises(ValueError, match="exactly one"):
        FakeProvider(responses=["x"], responder=mock_responder)


async def test_mock_responder_cites_a_provided_chunk_or_abstains() -> None:
    provider = FakeProvider(responder=mock_responder)
    with_context = _request('<chunk id="doc-0001">text</chunk>', purpose="answer")
    text = (await provider.complete(with_context)).text
    assert '"citations": ["doc-0001"]' in text
    assert '"abstain": false' in text
    text = (await provider.complete(_request("no chunks", purpose="answer"))).text
    assert '"abstain": true' in text
    with pytest.raises(LLMError, match="no template"):
        await provider.complete(_request("x", purpose="unknown"))


def test_cache_key_depends_on_every_request_field() -> None:
    base = _request("q")
    assert cache_key(base) == cache_key(_request("q"))
    assert cache_key(base) != cache_key(_request("q", model="other"))
    assert cache_key(base) != cache_key(base.model_copy(update={"max_tokens": 5}))
    assert cache_key(base) != cache_key(base.model_copy(update={"purpose": "other"}))
    assert cache_key(base) != cache_key(
        base.model_copy(update={"messages": [ChatMessage(role="user", content="other")]})
    )


async def test_cached_provider_hits_disk_on_repeat(tmp_path: Path) -> None:
    inner = FakeProvider(responses=["first", "second"])
    cached = CachedProvider(inner, tmp_path / "llm")
    a = await cached.complete(_request("same"))
    b = await cached.complete(_request("same"))
    c = await cached.complete(_request("different"))
    assert a.text == b.text == "first"
    assert a.cached is False
    assert b.cached is True
    assert c.text == "second"
    assert inner.calls == 2
    assert (cached.hits, cached.misses) == (1, 2)
    assert len(list((tmp_path / "llm").glob("*.json"))) == 2

    # A fresh wrapper over an empty inner provider is served entirely from disk.
    again = CachedProvider(FakeProvider(responses=[]), tmp_path / "llm")
    assert (await again.complete(_request("same"))).text == "first"
    assert again.name == "cached(fake)"
