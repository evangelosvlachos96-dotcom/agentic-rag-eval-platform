"""LLM: a thin provider interface over the Anthropic SDK.

Planned responsibilities (Milestone 4 onward):

- a small `LLMProvider` protocol so the rest of the code never imports a
  vendor SDK directly
- an async Anthropic implementation with retries, timeouts and usage tracking
- a deterministic fake provider for unit tests (no network, no API key)
"""
