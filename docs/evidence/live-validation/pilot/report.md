# Eval run `20261010T150853Z_live_pilot`

- config: `live_pilot`
- created: 2026-10-10T15:09:40+00:00
- git: `c1193279bda76c5d2ca549e84668607de824a111`
- dataset version: `27b46e65f45d`
- eval set: `v1` @ `1f48f2e04ef7` (4 items)
- prompts: {'answer': 'answer_v1', 'judge_faithfulness': 'judge_faithfulness_v1', 'judge_correctness': 'judge_correctness_v1', 'judge_relevance': 'judge_relevance_v1'}
- generator: `claude-sonnet-5`  judge: `claude-haiku-4-5`  provider: `cached(budgeted(anthropic))`
- retrieval only: False
- LLM calls: 13 (cache hits 0, misses 13); tokens in/out: 26060/2832; estimated cost: 0.059335
- errors: 0; items whose labels matched no chunk: 0
- bootstrap: 1000 resamples, seed 0

## Usage accounting

Token totals include cached responses; incremental cost excludes cache hits. Rates are applied separately per requested model. Hidden SDK retries and provider billing adjustments are not independently observable.

Calls with unknown usage: 0

| Model | Total input | Total output | Billable input | Billable output |
| --- | ---: | ---: | ---: | ---: |
| claude-haiku-4-5 | 11290 | 1963 | 11290 | 1963 |
| claude-sonnet-5 | 14770 | 869 | 14770 | 869 |

## Metrics

| metric | mean | 95% CI | n |
| --- | ---: | ---: | ---: |
| abstained | 0.250 | [0.000, 0.750] | 4 |
| answered_without_citations | 0.000 | [0.000, 0.000] | 3 |
| citations_valid | 1.000 | [1.000, 1.000] | 3 |
| correct_abstention | 1.000 | [1.000, 1.000] | 1 |
| correctness | 1.000 | [1.000, 1.000] | 3 |
| faithfulness | 1.000 | [1.000, 1.000] | 3 |
| hit@1 | 0.333 | [0.000, 1.000] | 3 |
| hit@8 | 1.000 | [1.000, 1.000] | 3 |
| missed_abstention | 0.000 | [0.000, 0.000] | 1 |
| mrr | 0.492 | [0.143, 1.000] | 3 |
| ndcg@8 | 0.391 | [0.137, 0.832] | 3 |
| precision@8 | 0.167 | [0.125, 0.250] | 3 |
| recall@8 | 0.548 | [0.143, 1.000] | 3 |
| relevance | 1.000 | [1.000, 1.000] | 3 |
| unnecessary_abstention | 0.000 | [0.000, 0.000] | 3 |

## By category

### conceptual

| metric | mean | 95% CI | n |
| --- | ---: | ---: | ---: |
| abstained | 0.000 | [0.000, 0.000] | 1 |
| answered_without_citations | 0.000 | [0.000, 0.000] | 1 |
| citations_valid | 1.000 | [1.000, 1.000] | 1 |
| correctness | 1.000 | [1.000, 1.000] | 1 |
| faithfulness | 1.000 | [1.000, 1.000] | 1 |
| hit@1 | 1.000 | [1.000, 1.000] | 1 |
| hit@8 | 1.000 | [1.000, 1.000] | 1 |
| mrr | 1.000 | [1.000, 1.000] | 1 |
| ndcg@8 | 0.832 | [0.832, 0.832] | 1 |
| precision@8 | 0.250 | [0.250, 0.250] | 1 |
| recall@8 | 1.000 | [1.000, 1.000] | 1 |
| relevance | 1.000 | [1.000, 1.000] | 1 |
| unnecessary_abstention | 0.000 | [0.000, 0.000] | 1 |

### exact_term

| metric | mean | 95% CI | n |
| --- | ---: | ---: | ---: |
| abstained | 0.000 | [0.000, 0.000] | 1 |
| answered_without_citations | 0.000 | [0.000, 0.000] | 1 |
| citations_valid | 1.000 | [1.000, 1.000] | 1 |
| correctness | 1.000 | [1.000, 1.000] | 1 |
| faithfulness | 1.000 | [1.000, 1.000] | 1 |
| hit@1 | 0.000 | [0.000, 0.000] | 1 |
| hit@8 | 1.000 | [1.000, 1.000] | 1 |
| mrr | 0.143 | [0.143, 0.143] | 1 |
| ndcg@8 | 0.204 | [0.204, 0.204] | 1 |
| precision@8 | 0.125 | [0.125, 0.125] | 1 |
| recall@8 | 0.500 | [0.500, 0.500] | 1 |
| relevance | 1.000 | [1.000, 1.000] | 1 |
| unnecessary_abstention | 0.000 | [0.000, 0.000] | 1 |

### multi_hop

| metric | mean | 95% CI | n |
| --- | ---: | ---: | ---: |
| abstained | 0.000 | [0.000, 0.000] | 1 |
| answered_without_citations | 0.000 | [0.000, 0.000] | 1 |
| citations_valid | 1.000 | [1.000, 1.000] | 1 |
| correctness | 1.000 | [1.000, 1.000] | 1 |
| faithfulness | 1.000 | [1.000, 1.000] | 1 |
| hit@1 | 0.000 | [0.000, 0.000] | 1 |
| hit@8 | 1.000 | [1.000, 1.000] | 1 |
| mrr | 0.333 | [0.333, 0.333] | 1 |
| ndcg@8 | 0.137 | [0.137, 0.137] | 1 |
| precision@8 | 0.125 | [0.125, 0.125] | 1 |
| recall@8 | 0.143 | [0.143, 0.143] | 1 |
| relevance | 1.000 | [1.000, 1.000] | 1 |
| unnecessary_abstention | 0.000 | [0.000, 0.000] | 1 |

### unanswerable

| metric | mean | 95% CI | n |
| --- | ---: | ---: | ---: |
| abstained | 1.000 | [1.000, 1.000] | 1 |
| correct_abstention | 1.000 | [1.000, 1.000] | 1 |
| missed_abstention | 0.000 | [0.000, 0.000] | 1 |

## Worst 0 failures

No failures by the report's scoring.
