"""A deterministic fake provider for tests and offline smoke runs.

:class:`FakeProvider` answers from a queue of canned texts, or from a
``responder`` callable that inspects the request, and records every request it
receives. :func:`mock_responder` returns schema-valid JSON for each call
``purpose`` so the whole eval pipeline can run without an API key. Anything it
produces is a placeholder, never a result.
"""

from __future__ import annotations

import json
from collections.abc import Callable, Sequence

from ragplatform.llm.provider import CompletionRequest, CompletionResponse, LLMError
from ragplatform.models import TokenUsage

Responder = Callable[[CompletionRequest], str]


class FakeProvider:
    """Replays canned responses in order, or delegates to ``responder``."""

    def __init__(
        self,
        responses: Sequence[str] | None = None,
        responder: Responder | None = None,
        model_name: str = "fake-model",
    ) -> None:
        if (responses is None) == (responder is None):
            raise ValueError("pass exactly one of responses or responder")
        self._queue = list(responses or [])
        self._responder = responder
        self._model_name = model_name
        self.requests: list[CompletionRequest] = []

    @property
    def name(self) -> str:
        return "fake"

    @property
    def calls(self) -> int:
        return len(self.requests)

    async def complete(self, request: CompletionRequest) -> CompletionResponse:
        self.requests.append(request)
        if self._responder is not None:
            text = self._responder(request)
        elif self._queue:
            text = self._queue.pop(0)
        else:
            raise LLMError("fake provider has no responses left")
        usage = TokenUsage(input_tokens=len(request.system) // 4, output_tokens=len(text) // 4)
        return CompletionResponse(
            text=text, model=self._model_name, usage=usage, stop_reason="end_turn"
        )


def _chunk_ids_in(request: CompletionRequest) -> list[str]:
    """Chunk ids mentioned in the user message as ``<chunk id="...">`` tags."""
    ids: list[str] = []
    for message in request.messages:
        start = 0
        while True:
            start = message.content.find('<chunk id="', start)
            if start == -1:
                break
            end = message.content.find('"', start + 11)
            ids.append(message.content[start + 11 : end])
            start = end
    return ids


def mock_responder(request: CompletionRequest) -> str:
    """Schema-valid placeholder JSON keyed on ``request.purpose``."""
    if request.purpose == "answer":
        ids = _chunk_ids_in(request)
        if not ids:
            return json.dumps({"answer": "", "citations": [], "abstain": True})
        return json.dumps(
            {
                "answer": f"Placeholder answer citing {ids[0]}.",
                "citations": ids[:1],
                "abstain": False,
            }
        )
    if request.purpose == "judge_faithfulness":
        return json.dumps(
            {
                "claims": [
                    {
                        "claim": "placeholder claim",
                        "evidence": "placeholder evidence",
                        "reasoning": "placeholder reasoning",
                        "supported": True,
                    }
                ]
            }
        )
    if request.purpose == "judge_correctness":
        return json.dumps({"evidence": "placeholder", "reasoning": "placeholder", "correct": True})
    if request.purpose == "judge_relevance":
        return json.dumps({"reasoning": "placeholder", "relevant": True})
    if request.purpose == "candidate":
        return json.dumps(
            {
                "question": "Placeholder question?",
                "reference_answer": "Placeholder answer.",
                "category": "lookup",
                "difficulty": "easy",
            }
        )
    raise LLMError(f"mock responder has no template for purpose {request.purpose!r}")
