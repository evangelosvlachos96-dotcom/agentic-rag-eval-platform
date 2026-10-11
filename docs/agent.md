# Bounded search agent

M6 implements a provider-independent JSON action loop: search, answer or abstain.
It can rewrite a query after inspecting retrieved evidence. Actions use the existing
completion protocol rather than vendor-specific native tool calls.

Each run records its configuration, provider, model, dataset, prompt version,
requests, raw responses, retrieved chunks, usage and stop reason. Citation IDs must
refer to evidence actually included in the bounded context. A malformed response,
unknown citation, repeated query or timeout ends the run without an answer.

The limits are explicit: maximum steps, per-call completion tokens, total **reserved
output tokens**, question length, evidence characters, chunk count and per-operation
timeout. Input token billing is not bounded by the output budget. A timed-out local
search thread may finish in the background. There are no hidden repair calls or
retries in the loop.

## Reproduce without API calls

```powershell
rag agent-demo "What do Required and NotRequired mean for TypedDict keys?" --rewrite "PEP 655 Required NotRequired Specification" --dataset-version 27b46e65f45d --output experiments/agent-demo.json
```

This command only constructs FakeProvider and local BM25 search, even when a real
API key exists. The saved demo in `docs/evidence/agent/offline-trajectory.json`
contains real retrieved passages, scripted search decisions and a placeholder answer.
It verifies integration, not model quality, autonomous reasoning or answer accuracy.

`agent.metrics` provides finite-sample pass@k (at least one success) and pass^k
(all k successes) estimators for k draws without replacement from n independent
attempts. Both require n >= k and an externally assessed success count. No real-agent
success rates are reported yet.

Four real-provider demonstrations were executed under the owner's shared budget:
three two-step search-and-answer trajectories and one single-step abstention.
See [live results](live-results.md) and `docs/evidence/live-validation/agents/`.
These demonstrate execution and citation structure, not a measured pass@k success rate.
