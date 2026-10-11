# Local showcase readiness

The M1–M9 local showcase implementation and the owner-authorized live pilot are
complete. Four retrieval configurations each answered the frozen 24-question set,
and four real agent demonstrations were saved. [Live results](live-results.md),
screenshots, source evidence and usage accounting are published on the static
results site. Human calibration and a broader held-out benchmark remain future
work; no production-readiness or human-certified accuracy claim is made.

## Verified

| Area | Evidence |
| --- | --- |
| Reviewed pilot | 24 owner-approved questions; 20 answerable and 4 unanswerable |
| Retrieval | Four configurations plus three BM25 chunking/header variants |
| Artifact integrity | Seven retrieval-only runs verified; four live runs checked against approved questions, coverage, metrics and bootstrap intervals, with result hashes |
| Agent | Offline boundary tests plus four real trajectories: three cited answers and one abstention |
| Data quality | Blank annotation export, validated import, failure signals and agreement calculations |
| API and container | Real local BM25 retrieval; generation rejected without explicit provider injection; non-root, read-only, network-disabled container smoke check |
| Cost safety | Shared USD 3 reservation budget, no SDK retries, provider-isolated cache, persistent usage and retained failed-call allowance |
| Full pipeline | Four configurations completed all 24 questions with real generation and judges; completed runs have no item errors, and the interrupted attempt remains archived |
| Automated checks | 193 offline tests passed, lint and strict type checks passed; two model tests excluded from the default suite |

The two real-model checks passed earlier with cached local models. They were not
rerun for changes confined to the agent, service, annotations or accounting.
GitHub CI records validation for each pushed implementation commit.

## Findings and limits

Hybrid has the highest observed Hit@8 in the frozen pilot (80%). Its improvement
over BM25 is inconclusive under the paired interval. Smaller BM25 chunks improve
Hit@1 while reducing Hit@8. These observations do not justify changing defaults.
See [retrieval](baseline-results.md), [chunking](chunking-results.md) and
[label sensitivity](label-sensitivity.md) reports and their screenshots.

Live judged correctness was 95% for BM25, 85% for vector, 95% for hybrid and 90%
for hybrid with reranking (20 answerable questions). All paired correctness
intervals against BM25 included zero. Every configuration abstained on all four
unanswerable questions. Faithfulness is measured only among generated answers;
these automated judgments have not been calibrated against independent human labels.

One confirmed missing source label has an assistant-proposed correction. It is
kept separate from the approved labels. The remaining 425-passage pooled review
packet is not an exhaustive or completed human relevance review. Broader review
and a held-out evaluation set are still needed for stronger quality claims.

The service is a local showcase, not a public production deployment. Authentication,
distributed rate limits, production load testing and operational SLOs are outside
this implementation. Repeated-trial agent success rates and human-judge
calibration remain unmeasured. Four trajectories demonstrate operation only.

## Completed paid validation

The owner authorized EUR 4 on 2026-10-10. The session recorded 326 completion
attempts with USD 1.4200 in reported token usage and USD 0.0120 retained for one
unmetered failed request. The combined USD 1.4320 remained below the conservative
USD 3 dispatch ceiling. The initial interrupted BM25 run is archived; recovery
reused cached responses and never refunded the unknown request.

The configured standard base-token rates were checked on 2026-10-10 against
[Anthropic's official pricing](https://platform.claude.com/docs/en/about-claude/pricing).
Live access to Sonnet 5 and Haiku 4.5 was verified. Token-cost estimates are not
invoice reconciliation. No further API calls are needed for this release.
See [cost accounting details](cost-safety.md).

Optional follow-up work requiring owner involvement: independent answer review,
proposed relevance additions, and human-judge agreement. A blank review packet
with real answers is prepared; human judgments have not been invented.

## Reproduce free verification

```powershell
uv sync --locked --extra api
uv run --extra api ruff check .
uv run --extra api ruff format --check .
uv run --extra api mypy
uv run --extra api pytest
uv run --extra api python scripts/verify_showcase.py
uv run --extra api python scripts/summarize_live_validation.py
uv run --extra api python scripts/build_results_page.py
```

Saved verification artifacts are under `docs/evidence/readiness`. The Docker smoke
script and API setup are documented in [infrastructure](infrastructure.md).
