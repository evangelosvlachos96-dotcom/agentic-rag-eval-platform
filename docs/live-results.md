# Live validation results

Real API evaluation on the frozen 24-question owner-approved PEP pilot. These are automated-judge measurements, not human-certified accuracy.

Generator: Claude Sonnet 5. Judges: Claude Haiku 4.5. Same prompts, dataset and generation settings across four retrieval configurations.

| Configuration | Correctness (n) | 95% bootstrap CI | Faithfulness (n) | Correct abstention (n) |
| --- | --- | --- | --- | --- |
| bm25_only | 95% (20) | [85%, 100%] | 92.3% (19) | 100% (4) |
| vector_only | 85% (20) | [70%, 100%] | 100.0% (17) | 100% (4) |
| hybrid | 95% (20) | [85%, 100%] | 93.4% (19) | 100% (4) |
| hybrid_rerank | 90% (20) | [75%, 100%] | 94.5% (18) | 100% (4) |

Correctness includes zero for unnecessary abstention on answerable questions. Faithfulness is the mean supported-claim fraction among answers judged; abstentions are excluded. Correct abstention uses the four unanswerable questions.
An all-success bootstrap interval does not establish perfect population accuracy. Labeled-source retrieval hits and automated answer judgments measure different properties; neither substitutes for independent human review.

## Cost and execution

326 API completion attempts; 581,540 input and 78,588 output tokens. Estimated reported token cost **USD 1.4200**, plus **USD 0.0120 retained for unmetered failures (n=1)**, including the preliminary pilot and agent demonstrations. All dispatch reservations stayed within the shared USD 3 ceiling. Token totals exclude unmetered failures. Actual billing remains the account invoice's authority.

The pilot's identical requests can be cache hits in the full BM25 run. The session ledger counts each paid request once; cached outputs are not independent repeated trials. No repeated attempts were made to select favorable results.

An initial provider failure interrupted BM25 evaluation. The stopped run is retained under `interrupted-attempts`; recovery kept the entire failed-call allowance, reused completed responses, and paced subsequent requests. The original failure cause was not recorded beyond LLMError; it is not assumed to be free.

## Paired correctness comparisons against BM25

- vector_only: delta -10.0%; 95% CI [-25.0%, +0.0%].
- hybrid: delta +0.0%; 95% CI [+0.0%, +0.0%].
- hybrid_rerank: delta -5.0%; 95% CI [-15.0%, +0.0%].

1,000 paired bootstrap resamples, seed 0. Exploratory comparisons without multiplicity correction; related questions and incomplete labels limit generalization.

## Agent demonstrations

- Does PEP 484 require Python to enforce type hints at runtime? — answered; 2 step(s).
- Why does PEP 526 favor annotation syntax over type comments for parsing? — answered; 2 step(s).
- Which PEP defines the field-annotation syntax used by data classes, and what limitation does it identify for type comments on uninitialized variables? — answered; 2 step(s).
- What is this RAG platform's production database password? — abstained; 1 step(s).

Single bounded attempts with real BM25 search. Structural citation checks do not establish factual correctness, and four trajectories are not a pass@k study.

## Review and provenance

Full answers, judge reasoning, citations and run reports are in [the evidence archive](evidence/live-validation/). `analysis.json` records verified result hashes, recalculated bootstrap intervals and paired comparisons. `human-review-blank.json` is prepared for review; no human verdicts are invented.

The run summaries retain commit and dirty-working-tree provenance. `execution-changes.patch` records the budget-recovery and pacing changes relative to the recorded base commit; evaluation prompts and model settings were unchanged during recovery.

Human-judge calibration, broader relevance review and a separate held-out benchmark remain uncompleted. This is a completed small live validation, not proof of production readiness.
