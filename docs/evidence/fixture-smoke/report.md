# Eval run `20261005T021647Z_bm25_only`

- config: `bm25_only`
- created: 2026-10-05T02:16:48+00:00
- git: `0285de60ada9e8a66dc5dcabe834736f09710702` (dirty)
- dataset version: `d3d5a78cb0d2`
- eval set: `fixture` @ `a183681ae7db` (5 items)
- prompts: {'answer': 'answer_v1', 'judge_faithfulness': 'judge_faithfulness_v1', 'judge_correctness': 'judge_correctness_v1', 'judge_relevance': 'judge_relevance_v1'}
- generator: `None`  judge: `None`  provider: `None`
- retrieval only: True
- LLM calls: 0 (cache hits 0, misses 0); tokens in/out: 0/0; estimated cost: n/a
- errors: 0; items whose labels matched no chunk: 0
- bootstrap: 1000 resamples, seed 0

## Metrics

| metric | mean | 95% CI | n |
| --- | ---: | ---: | ---: |
| hit@1 | 1.000 | [1.000, 1.000] | 4 |
| hit@8 | 1.000 | [1.000, 1.000] | 4 |
| mrr | 1.000 | [1.000, 1.000] | 4 |
| ndcg@8 | 1.000 | [1.000, 1.000] | 4 |
| precision@8 | 0.125 | [0.125, 0.125] | 4 |
| recall@8 | 1.000 | [1.000, 1.000] | 4 |

## By category

### conceptual

| metric | mean | 95% CI | n |
| --- | ---: | ---: | ---: |
| hit@1 | 1.000 | [1.000, 1.000] | 1 |
| hit@8 | 1.000 | [1.000, 1.000] | 1 |
| mrr | 1.000 | [1.000, 1.000] | 1 |
| ndcg@8 | 1.000 | [1.000, 1.000] | 1 |
| precision@8 | 0.125 | [0.125, 0.125] | 1 |
| recall@8 | 1.000 | [1.000, 1.000] | 1 |

### exact_term

| metric | mean | 95% CI | n |
| --- | ---: | ---: | ---: |
| hit@1 | 1.000 | [1.000, 1.000] | 1 |
| hit@8 | 1.000 | [1.000, 1.000] | 1 |
| mrr | 1.000 | [1.000, 1.000] | 1 |
| ndcg@8 | 1.000 | [1.000, 1.000] | 1 |
| precision@8 | 0.125 | [0.125, 0.125] | 1 |
| recall@8 | 1.000 | [1.000, 1.000] | 1 |

### lookup

| metric | mean | 95% CI | n |
| --- | ---: | ---: | ---: |
| hit@1 | 1.000 | [1.000, 1.000] | 2 |
| hit@8 | 1.000 | [1.000, 1.000] | 2 |
| mrr | 1.000 | [1.000, 1.000] | 2 |
| ndcg@8 | 1.000 | [1.000, 1.000] | 2 |
| precision@8 | 0.125 | [0.125, 0.125] | 2 |
| recall@8 | 1.000 | [1.000, 1.000] | 2 |

### unanswerable

| metric | mean | 95% CI | n |
| --- | ---: | ---: | ---: |

## Worst 0 failures

No failures by the report's scoring.
