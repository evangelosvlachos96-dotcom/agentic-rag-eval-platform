# Local showcase readiness

The M1–M9 local implementation is complete. Real retrieval experiments, offline
agent/evaluation tests, annotation tooling and container verification are saved in
this repository. **Paid answer and agent evaluation has not been run.** Development
had stopped at that spending boundary. On 2026-10-10 the owner approved a EUR 4
validation budget; the [bounded live workflow](live-validation.md) is prepared,
but execution is blocked by the missing local API credential.

## Verified

| Area | Evidence |
| --- | --- |
| Reviewed pilot | 24 owner-approved questions; 20 answerable and 4 unanswerable |
| Retrieval | Four configurations plus three BM25 chunking/header variants |
| Artifact integrity | Seven saved runs checked against approved questions, source flags, metrics and bootstrap intervals |
| Agent | Bounded multi-step search, rewritten queries, citations, abstention and failure paths tested with fake completions |
| Data quality | Blank annotation export, validated import, failure signals and agreement calculations |
| API and container | Real local BM25 retrieval; generation rejected without explicit provider injection; non-root, read-only, network-disabled container smoke check |
| Cost safety | Provider-free dry run, provider-isolated cache and per-model usage accounting |
| Full pipeline | All 24 pilot questions completed through fake generation and judges with no errors; placeholder integration evidence only |
| Automated checks | 185 offline tests passed, lint and strict type checks passed; two model tests excluded from the default suite |

The two real-model checks passed earlier with cached local models. They were not
rerun for changes confined to the agent, service, annotations or accounting.
GitHub CI also passed for the implementation and cost-safety commits.

## Findings and limits

Hybrid has the highest observed Hit@8 in the frozen pilot (80%). Its improvement
over BM25 is inconclusive under the paired interval. Smaller BM25 chunks improve
Hit@1 while reducing Hit@8. These observations do not justify changing defaults.
See [retrieval](baseline-results.md), [chunking](chunking-results.md) and
[label sensitivity](label-sensitivity.md) reports and their screenshots.

One confirmed missing source label has an assistant-proposed correction. It is
kept separate from the approved labels. The remaining 425-passage pooled review
packet is not an exhaustive or completed human relevance review. Broader review
and a held-out evaluation set are still needed for stronger quality claims.

The service is a local showcase, not a public production deployment. Authentication,
distributed rate limits, production load testing and operational SLOs are outside
this implementation. Real-answer accuracy, faithfulness, abstention quality, agent
success rates and human–judge calibration remain unmeasured.

## Paid-evaluation boundary

A provider-free dry run over the 24-question BM25 pilot plans approximately 92
completion calls, 149,096 input tokens and 25,880 output tokens using fixed typical
output allowances. Repairs and SDK retries can add calls and tokens; this is not a
hard limit or guaranteed bill. Start with a small explicitly approved pilot, inspect
its real usage and outputs, and only then consider a larger run.

The configured standard base-token rates were checked on 2026-10-05 against
[Anthropic's official pricing](https://platform.claude.com/docs/en/about-claude/pricing).
The public documentation still lists the configured legacy model IDs. Account
access and actual generation behavior have not been tested. No provider credentials
were used to make paid requests. See [cost accounting details](cost-safety.md).

Remaining work requiring owner involvement: approve a paid model/budget when ready,
review real answers and proposed relevance additions, then interpret the measured
results. Human labels must not be invented to make the project appear finished.

## Reproduce free verification

```powershell
uv sync --locked --extra api
uv run --extra api ruff check .
uv run --extra api ruff format --check .
uv run --extra api mypy
uv run --extra api pytest
uv run --extra api python scripts/verify_showcase.py
```

Saved verification artifacts are under `docs/evidence/readiness`. The Docker smoke
script and API setup are documented in [infrastructure](infrastructure.md).
