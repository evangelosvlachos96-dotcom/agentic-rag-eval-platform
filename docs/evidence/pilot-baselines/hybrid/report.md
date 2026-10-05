# Eval run `20261005T033936Z_hybrid`

- config: `hybrid`
- created: 2026-10-05T03:39:40+00:00
- git: `0285de60ada9e8a66dc5dcabe834736f09710702` (dirty)
- dataset version: `27b46e65f45d`
- eval set: `v1` @ `1f48f2e04ef7` (24 items)
- prompts: {'answer': 'answer_v1', 'judge_faithfulness': 'judge_faithfulness_v1', 'judge_correctness': 'judge_correctness_v1', 'judge_relevance': 'judge_relevance_v1'}
- generator: `None`  judge: `None`  provider: `None`
- retrieval only: True
- LLM calls: 0 (cache hits 0, misses 0); tokens in/out: 0/0; estimated cost: n/a
- errors: 0; items whose labels matched no chunk: 0
- bootstrap: 1000 resamples, seed 0

## Metrics

| metric | mean | 95% CI | n |
| --- | ---: | ---: | ---: |
| hit@1 | 0.400 | [0.200, 0.600] | 20 |
| hit@8 | 0.800 | [0.600, 0.950] | 20 |
| mrr | 0.562 | [0.392, 0.733] | 20 |
| ndcg@8 | 0.515 | [0.357, 0.665] | 20 |
| precision@8 | 0.138 | [0.100, 0.175] | 20 |
| recall@8 | 0.639 | [0.450, 0.804] | 20 |

## By category

### comparison

| metric | mean | 95% CI | n |
| --- | ---: | ---: | ---: |
| hit@1 | 0.250 | [0.000, 0.750] | 4 |
| hit@8 | 0.500 | [0.000, 1.000] | 4 |
| mrr | 0.333 | [0.000, 0.750] | 4 |
| ndcg@8 | 0.378 | [0.000, 0.755] | 4 |
| precision@8 | 0.125 | [0.000, 0.250] | 4 |
| recall@8 | 0.500 | [0.000, 1.000] | 4 |

### conceptual

| metric | mean | 95% CI | n |
| --- | ---: | ---: | ---: |
| hit@1 | 0.500 | [0.000, 1.000] | 4 |
| hit@8 | 1.000 | [1.000, 1.000] | 4 |
| mrr | 0.750 | [0.500, 1.000] | 4 |
| ndcg@8 | 0.724 | [0.509, 0.939] | 4 |
| precision@8 | 0.156 | [0.125, 0.219] | 4 |
| recall@8 | 0.875 | [0.625, 1.000] | 4 |

### exact_term

| metric | mean | 95% CI | n |
| --- | ---: | ---: | ---: |
| hit@1 | 0.250 | [0.000, 0.750] | 4 |
| hit@8 | 0.750 | [0.250, 1.000] | 4 |
| mrr | 0.438 | [0.125, 0.812] | 4 |
| ndcg@8 | 0.454 | [0.108, 0.847] | 4 |
| precision@8 | 0.094 | [0.031, 0.125] | 4 |
| recall@8 | 0.625 | [0.250, 1.000] | 4 |

### lookup

| metric | mean | 95% CI | n |
| --- | ---: | ---: | ---: |
| hit@1 | 0.250 | [0.000, 0.750] | 4 |
| hit@8 | 0.750 | [0.250, 1.000] | 4 |
| mrr | 0.458 | [0.125, 0.750] | 4 |
| ndcg@8 | 0.533 | [0.158, 0.815] | 4 |
| precision@8 | 0.094 | [0.031, 0.125] | 4 |
| recall@8 | 0.750 | [0.250, 1.000] | 4 |

### multi_hop

| metric | mean | 95% CI | n |
| --- | ---: | ---: | ---: |
| hit@1 | 0.750 | [0.250, 1.000] | 4 |
| hit@8 | 1.000 | [1.000, 1.000] | 4 |
| mrr | 0.833 | [0.500, 1.000] | 4 |
| ndcg@8 | 0.485 | [0.337, 0.632] | 4 |
| precision@8 | 0.219 | [0.156, 0.250] | 4 |
| recall@8 | 0.446 | [0.310, 0.583] | 4 |

### unanswerable

| metric | mean | 95% CI | n |
| --- | ---: | ---: | ---: |

## Worst 4 failures

### pilot-002 (exact_term, answerable)

**Question:** According to PEP 604, what does X | Y mean in a type annotation?

**Reference:** A union type, equivalent to Union[X, Y].

**Retrieved sections:**

- ❌ [1] Syntax for Variable Annotations > Rejected/Postponed Proposals (`4e9bac3fbbd66adf-0020`)
- ❌ [2] Deferred Evaluation Of Annotations Using Descriptors > Overview > Comparison Of Annotation Semantics (`ad23617867325d80-0005`)
- ❌ [3] Deferred Evaluation Of Annotations Using Descriptors > Overview > Comparison Of Annotation Semantics (`ad23617867325d80-0006`)
- ❌ [4] Allow writing union types as ``X | Y`` > Motivation (`1b96f779896ff109-0002`)
- ❌ [5] Deferred Evaluation Of Annotations Using Descriptors > Overview > Comparison Of Annotation Semantics (`ad23617867325d80-0007`)
- ❌ [6] Syntax for Variable Annotations > Specification (`4e9bac3fbbd66adf-0006`)
- ❌ [7] Implementing PEP 649 > Behavior of dataclass field types (`80014392886f031e-0039`)
- ❌ [8] Flexible function and variable annotations > Motivation (`18ed3b62aa90c0eb-0002`)

**Metrics:** hit@1=0.00, hit@8=0.00, mrr=0.00, ndcg@8=0.00, precision@8=0.00, recall@8=0.00

### pilot-006 (lookup, answerable)

**Question:** Which methods form the context-manager protocol described by PEP 343?

**Reference:** The methods __enter__() and __exit__().

**Retrieved sections:**

- ❌ [1] Coroutines with async and await syntax > Specification > Asynchronous Context Managers and "async with" (`b6d5d84d24a46b97-0014`)
- ❌ [2] The "with" Statement > Resolved Issues (`9b8996160cdfb03e-0022`)
- ❌ [3] Coroutines with async and await syntax > Specification > Asynchronous Context Managers and "async with" > New Syntax (`b6d5d84d24a46b97-0015`)
- ❌ [4] Protocols: Structural subtyping (static duck typing) > Rationale and Goals > Non-goals (`a35c304214b4044a-0005`)
- ❌ [5] The "with" Statement > Standard Terminology (`9b8996160cdfb03e-0019`)
- ❌ [6] The "with" Statement > Caching Context Managers (`9b8996160cdfb03e-0020`)
- ❌ [7] The "with" Statement > Examples (`9b8996160cdfb03e-0030`)
- ❌ [8] Protocols: Structural subtyping (static duck typing) > Specification > Terminology (`a35c304214b4044a-0010`)

**Metrics:** hit@1=0.00, hit@8=0.00, mrr=0.00, ndcg@8=0.00, precision@8=0.00, recall@8=0.00

### pilot-013 (comparison, answerable)

**Question:** What type-annotation features do PEP 585 and PEP 604 add?

**Reference:** PEP 585 adds generic parameter syntax to standard collections; PEP 604 adds X | Y syntax for union types.

**Retrieved sections:**

- ❌ [1] Flexible function and variable annotations > Motivation (`18ed3b62aa90c0eb-0002`)
- ❌ [2] Implementing PEP 649 > Abstract (`80014392886f031e-0002`)
- ❌ [3] Deferred Evaluation Of Annotations Using Descriptors > Motivation > The Current State Of Annotation Use Cases > Static typing users (`ad23617867325d80-0013`)
- ❌ [4] Deferred Evaluation Of Annotations Using Descriptors > Motivation > The Current State Of Annotation Use Cases > Static typing users (`ad23617867325d80-0014`)
- ❌ [5] Deferred Evaluation Of Annotations Using Descriptors > Motivation > The Current State Of Annotation Use Cases > Runtime annotation users (`ad23617867325d80-0015`)
- ❌ [6] Deferred Evaluation Of Annotations Using Descriptors > Motivation > A History Of Annotations (`ad23617867325d80-0009`)
- ❌ [7] Postponed Evaluation of Annotations > Resolution (`24cedd106580f3ea-0001`)
- ❌ [8] Allow writing union types as ``X | Y`` > Motivation (`1b96f779896ff109-0002`)

**Metrics:** hit@1=0.00, hit@8=0.00, mrr=0.00, ndcg@8=0.00, precision@8=0.00, recall@8=0.00

### pilot-015 (comparison, answerable)

**Question:** Where do PEP 621 and PEP 723 place metadata?

**Reference:** PEP 621 places project core metadata in pyproject.toml; PEP 723 embeds script metadata in the script itself.

**Retrieved sections:**

- ❌ [1] Inline script metadata (`4ef54cafa35d2932-0000`)
- ❌ [2] Storing project metadata in pyproject.toml (`74f7628b9d5e0341-0000`)
- ❌ [3] Version Identification and Dependency Specification > Version scheme > Version ordering across different metadata versions (`a5feae5ef825dc18-0035`)
- ❌ [4] Inline script metadata > Rejected Ideas > Why not use a comment block resembling requirements.txt? (`4ef54cafa35d2932-0022`)
- ❌ [5] Storing project metadata in pyproject.toml > Motivation (`74f7628b9d5e0341-0003`)
- ❌ [6] Storing project metadata in pyproject.toml > Rejected Ideas > Support for a metadata provider (`74f7628b9d5e0341-0031`)
- ❌ [7] Version Identification and Dependency Specification > Summary of differences from PEP 386 (`a5feae5ef825dc18-0057`)
- ❌ [8] Inline script metadata > Rejected Ideas > Why not reuse core metadata fields? (`4ef54cafa35d2932-0024`)

**Metrics:** hit@1=0.00, hit@8=0.00, mrr=0.00, ndcg@8=0.00, precision@8=0.00, recall@8=0.00
