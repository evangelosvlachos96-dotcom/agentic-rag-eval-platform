"""LLM: a thin provider interface over the Anthropic SDK.

- ``provider``: :class:`LLMProvider` protocol plus the request / response models
- ``anthropic_provider``: the async Anthropic implementation (the only module
  that imports the vendor SDK)
- ``fake``: a deterministic provider for unit tests and offline smoke runs
- ``cache``: a content-addressed disk cache wrapping any provider
- ``structured``: JSON outputs validated with pydantic, with one repair retry
- ``pricing``: per-model prices from ``configs/pricing.yaml`` and cost estimates
"""

from ragplatform.llm.cache import CachedProvider
from ragplatform.llm.fake import FakeProvider, mock_responder
from ragplatform.llm.pricing import Pricing, load_pricing
from ragplatform.llm.provider import (
    ChatMessage,
    CompletionRequest,
    CompletionResponse,
    LLMError,
    LLMProvider,
)
from ragplatform.llm.structured import StructuredOutputError, complete_structured

__all__ = [
    "CachedProvider",
    "ChatMessage",
    "CompletionRequest",
    "CompletionResponse",
    "FakeProvider",
    "LLMError",
    "LLMProvider",
    "Pricing",
    "StructuredOutputError",
    "complete_structured",
    "load_pricing",
    "mock_responder",
]
