# Eval run `20261005T033932Z_vector_only`

- config: `vector_only`
- created: 2026-10-05T03:39:36+00:00
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
| hit@1 | 0.250 | [0.050, 0.450] | 20 |
| hit@8 | 0.750 | [0.550, 0.950] | 20 |
| mrr | 0.430 | [0.264, 0.589] | 20 |
| ndcg@8 | 0.443 | [0.281, 0.604] | 20 |
| precision@8 | 0.131 | [0.094, 0.169] | 20 |
| recall@8 | 0.606 | [0.414, 0.792] | 20 |

## By category

### comparison

| metric | mean | 95% CI | n |
| --- | ---: | ---: | ---: |
| hit@1 | 0.250 | [0.000, 0.750] | 4 |
| hit@8 | 0.500 | [0.000, 1.000] | 4 |
| mrr | 0.312 | [0.000, 0.750] | 4 |
| ndcg@8 | 0.367 | [0.000, 0.750] | 4 |
| precision@8 | 0.125 | [0.000, 0.250] | 4 |
| recall@8 | 0.500 | [0.000, 1.000] | 4 |

### conceptual

| metric | mean | 95% CI | n |
| --- | ---: | ---: | ---: |
| hit@1 | 0.000 | [0.000, 0.000] | 4 |
| hit@8 | 1.000 | [1.000, 1.000] | 4 |
| mrr | 0.411 | [0.232, 0.500] | 4 |
| ndcg@8 | 0.489 | [0.360, 0.618] | 4 |
| precision@8 | 0.156 | [0.125, 0.219] | 4 |
| recall@8 | 0.875 | [0.625, 1.000] | 4 |

### exact_term

| metric | mean | 95% CI | n |
| --- | ---: | ---: | ---: |
| hit@1 | 0.500 | [0.000, 1.000] | 4 |
| hit@8 | 0.750 | [0.250, 1.000] | 4 |
| mrr | 0.550 | [0.100, 1.000] | 4 |
| ndcg@8 | 0.559 | [0.119, 1.000] | 4 |
| precision@8 | 0.094 | [0.031, 0.125] | 4 |
| recall@8 | 0.625 | [0.250, 1.000] | 4 |

### lookup

| metric | mean | 95% CI | n |
| --- | ---: | ---: | ---: |
| hit@1 | 0.250 | [0.000, 0.750] | 4 |
| hit@8 | 0.500 | [0.000, 1.000] | 4 |
| mrr | 0.312 | [0.000, 0.750] | 4 |
| ndcg@8 | 0.358 | [0.000, 0.750] | 4 |
| precision@8 | 0.062 | [0.000, 0.125] | 4 |
| recall@8 | 0.500 | [0.000, 1.000] | 4 |

### multi_hop

| metric | mean | 95% CI | n |
| --- | ---: | ---: | ---: |
| hit@1 | 0.250 | [0.000, 0.750] | 4 |
| hit@8 | 1.000 | [1.000, 1.000] | 4 |
| mrr | 0.562 | [0.375, 0.875] | 4 |
| ndcg@8 | 0.441 | [0.208, 0.694] | 4 |
| precision@8 | 0.219 | [0.156, 0.250] | 4 |
| recall@8 | 0.530 | [0.226, 0.833] | 4 |

### unanswerable

| metric | mean | 95% CI | n |
| --- | ---: | ---: | ---: |

## Worst 5 failures

### pilot-002 (exact_term, answerable)

**Question:** According to PEP 604, what does X | Y mean in a type annotation?

**Reference:** A union type, equivalent to Union[X, Y].

**Retrieved sections:**

- ❌ [1] Flexible function and variable annotations > Motivation (`18ed3b62aa90c0eb-0002`)
- ❌ [2] Type Hints > Rationale and Goals (`a25e032f504686c8-0003`)
- ❌ [3] Deferred Evaluation Of Annotations Using Descriptors > Backwards Compatibility > Backwards Compatibility With PEP 563 Semantics (`ad23617867325d80-0054`)
- ❌ [4] Syntax for Variable Annotations > Abstract (`4e9bac3fbbd66adf-0003`)
- ❌ [5] Deferred Evaluation Of Annotations Using Descriptors > Overview > Comparison Of Annotation Semantics (`ad23617867325d80-0006`)
- ❌ [6] Allow writing union types as ``X | Y`` > Objections and responses > 2. Change only PEP 484 (Type hints) to accept the syntax ``type1 | type2`` ? (`1b96f779896ff109-0010`)
- ❌ [7] Type Hints > Abstract (`a25e032f504686c8-0001`)
- ❌ [8] Postponed Evaluation of Annotations > Rationale and Goals > Non-typing usage of annotations (`24cedd106580f3ea-0005`)

**Metrics:** hit@1=0.00, hit@8=0.00, mrr=0.00, ndcg@8=0.00, precision@8=0.00, recall@8=0.00

### pilot-006 (lookup, answerable)

**Question:** Which methods form the context-manager protocol described by PEP 343?

**Reference:** The methods __enter__() and __exit__().

**Retrieved sections:**

- ❌ [1] Coroutines with async and await syntax > Specification > Asynchronous Context Managers and "async with" (`b6d5d84d24a46b97-0014`)
- ❌ [2] The "with" Statement > Resolved Issues (`9b8996160cdfb03e-0022`)
- ❌ [3] The "with" Statement > Reference Implementation (`9b8996160cdfb03e-0031`)
- ❌ [4] Protocols: Structural subtyping (static duck typing) > Rejected/Postponed Ideas > Make protocols interoperable with other approaches (`a35c304214b4044a-0042`)
- ❌ [5] Protocols: Structural subtyping (static duck typing) > Rationale and Goals > Non-goals (`a35c304214b4044a-0005`)
- ❌ [6] PEP Purpose and Guidelines > What belongs in a successful PEP? (`97585c9eb60883b7-0024`)
- ❌ [7] PEP Purpose and Guidelines > What belongs in a successful PEP? (`97585c9eb60883b7-0023`)
- ❌ [8] Coroutines with async and await syntax > Specification > Asynchronous Context Managers and "async with" > New Syntax (`b6d5d84d24a46b97-0015`)

**Metrics:** hit@1=0.00, hit@8=0.00, mrr=0.00, ndcg@8=0.00, precision@8=0.00, recall@8=0.00

### pilot-007 (lookup, answerable)

**Question:** Which file does PEP 621 use for project core metadata?

**Reference:** pyproject.toml.

**Retrieved sections:**

- ❌ [1] Inline script metadata > Rejected Ideas > Why not reuse core metadata fields? (`4ef54cafa35d2932-0024`)
- ❌ [2] Storing project metadata in pyproject.toml > Motivation (`74f7628b9d5e0341-0003`)
- ❌ [3] Storing project metadata in pyproject.toml (`74f7628b9d5e0341-0000`)
- ❌ [4] Storing project metadata in pyproject.toml > Specification > Details > ``dynamic`` (`74f7628b9d5e0341-0022`)
- ❌ [5] Version Identification and Dependency Specification > Version scheme > Version ordering across different metadata versions (`a5feae5ef825dc18-0035`)
- ❌ [6] Inline script metadata > Rationale (`4ef54cafa35d2932-0003`)
- ❌ [7] Storing project metadata in pyproject.toml > Rejected Ideas > Support for a metadata provider (`74f7628b9d5e0341-0031`)
- ❌ [8] Storing project metadata in pyproject.toml > Reference Implementation (`74f7628b9d5e0341-0027`)

**Metrics:** hit@1=0.00, hit@8=0.00, mrr=0.00, ndcg@8=0.00, precision@8=0.00, recall@8=0.00

### pilot-013 (comparison, answerable)

**Question:** What type-annotation features do PEP 585 and PEP 604 add?

**Reference:** PEP 585 adds generic parameter syntax to standard collections; PEP 604 adds X | Y syntax for union types.

**Retrieved sections:**

- ❌ [1] Flexible function and variable annotations > Motivation (`18ed3b62aa90c0eb-0002`)
- ❌ [2] Implementing PEP 649 > How to Teach This (`80014392886f031e-0053`)
- ❌ [3] Flexible function and variable annotations > Abstract (`18ed3b62aa90c0eb-0001`)
- ❌ [4] Implementing PEP 649 > Deferred evaluation of PEP 695 and 696 objects (`80014392886f031e-0037`)
- ❌ [5] Type Hints > Rationale and Goals (`a25e032f504686c8-0003`)
- ❌ [6] Deferred Evaluation Of Annotations Using Descriptors > Motivation > The Current State Of Annotation Use Cases > Static typing users (`ad23617867325d80-0014`)
- ❌ [7] Postponed Evaluation of Annotations > Rationale and Goals > Non-typing usage of annotations (`24cedd106580f3ea-0005`)
- ❌ [8] Implementing PEP 649 > Abstract (`80014392886f031e-0002`)

**Metrics:** hit@1=0.00, hit@8=0.00, mrr=0.00, ndcg@8=0.00, precision@8=0.00, recall@8=0.00

### pilot-015 (comparison, answerable)

**Question:** Where do PEP 621 and PEP 723 place metadata?

**Reference:** PEP 621 places project core metadata in pyproject.toml; PEP 723 embeds script metadata in the script itself.

**Retrieved sections:**

- ❌ [1] Inline script metadata (`4ef54cafa35d2932-0000`)
- ❌ [2] Version Identification and Dependency Specification > Version scheme > Version ordering across different metadata versions (`a5feae5ef825dc18-0035`)
- ❌ [3] Storing project metadata in pyproject.toml > Rejected Ideas > Using structured TOML dictionaries to specify dependencies (`74f7628b9d5e0341-0043`)
- ❌ [4] Version Identification and Dependency Specification > Summary of differences from PEP 386 (`a5feae5ef825dc18-0057`)
- ❌ [5] Storing project metadata in pyproject.toml (`74f7628b9d5e0341-0000`)
- ❌ [6] Version Identification and Dependency Specification > Summary of differences from PEP 386 > Changing the version scheme (`a5feae5ef825dc18-0059`)
- ❌ [7] Inline script metadata > Rejected Ideas > Why not use a comment block resembling requirements.txt? (`4ef54cafa35d2932-0022`)
- ❌ [8] Version Identification and Dependency Specification > Summary of changes to PEP 440 (`a5feae5ef825dc18-0073`)

**Metrics:** hit@1=0.00, hit@8=0.00, mrr=0.00, ndcg@8=0.00, precision@8=0.00, recall@8=0.00
