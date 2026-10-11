# Budgeted live validation

On 2026-10-10 the owner authorized up to EUR 4 of Anthropic API usage for final
validation. The owner restored `ANTHROPIC_API_KEY` locally and live API access
was verified. Credentials remain local and must
never be pasted into reports, screenshots or GitHub.

The suite completed: four 24-question configurations and four agent demonstrations.
See the [verified results](live-results.md), including the retained interrupted run
and separate reported-cost and unknown-cost accounting. No further paid runs are
needed for this release.

## Prepared protocol

1. Run four approved pilot questions, including an unanswerable question.
2. If the pilot completes without errors, evaluate all 24 approved questions with
   BM25, vector, hybrid and hybrid with reranking.
3. Run four bounded agent demonstrations using BM25 search. Single attempts do
   not estimate pass@k or prove factual correctness.
4. Save full run artifacts, agent trajectories and a credential-free usage ledger.
   Rebuild the static page and screenshots from those artifacts.

Generator: `claude-sonnet-5`. Judges: `claude-haiku-4-5`. Generation and judge
outputs are limited to 1,536 tokens per call. Their standard rates were checked
on 2026-10-10 against [Anthropic pricing](https://platform.claude.com/docs/en/about-claude/pricing).
Model access still needs live verification; no silent model substitution is made.

The suite shares a conservative **USD 3 dispatch ceiling**, below the authorized
EUR allowance with a margin. Before every completion, the API's token-count
endpoint supplies an input estimate; the guard reserves 120% of that count plus
1,024 input tokens and the maximum output allowance. The reservation is written
to disk before sending the request and reconciled with reported usage afterward.
Unknown prices, insufficient funds, uncertain usage, interruption or an exceeded
reservation stop automatic progress. SDK retries are disabled. Structured-output
repair calls pass through the same guard. No caching or geographic billing
modifiers are requested. Taxes, foreign exchange and account-level adjustments
remain outside the token-usage estimate; this is not an invoice guarantee.

The session lock prevents concurrent runs. A crash deliberately leaves that lock
in place. Inspect the ledger before recovering a session; do not blindly delete
the lock or reset the ledger. When account usage cannot resolve a failed request,
an explicit operator recovery may retain its entire maximum allowance against
the original budget. This cannot clear a reservation overrun. The stopped process
must be confirmed before archiving its lock. The `--resume-retaining-reservations`
option archives interrupted evidence, preserves successful phases, and adds a
recovery note to each unmetered attempt. It never assumes that failure was free.
Subsequent paid requests are spaced by five seconds. Existing evidence is never
overwritten automatically. Previously completed responses can be reused from
the dedicated real-provider cache without charging again.

## Run locally

Make the key available in the process environment securely, then:

```powershell
.venv\Scripts\python.exe scripts/run_live_validation.py
.venv\Scripts\python.exe scripts/run_live_validation.py --execute
.venv\Scripts\python.exe scripts/build_results_page.py
```

The first command only prints the plan. The second can spend money and must only
be run under the owner's recorded budget authorization. Do not run the ordinary
unbounded evaluation CLI instead of this budgeted workflow for this session.

The static GitHub Pages source is `docs/index.html`, built from saved evidence.
`scripts/render_results_page.cjs` captures real desktop/mobile screenshots and
checks local links and horizontal overflow. The public page contains no API key
or visitor-triggered API calls. GitHub Pages serves the `main` branch's `/docs`.

Human answer review, human-judge calibration and a separate held-out evaluation
remain distinct tasks. Automated results will be labeled as such; this workflow
does not fabricate human approval or hide failed runs.
