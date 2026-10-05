# Eval run `20261005T033941Z_hybrid_rerank`

- config: `hybrid_rerank`
- created: 2026-10-05T03:44:53+00:00
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
| hit@1 | 0.350 | [0.150, 0.550] | 20 |
| hit@8 | 0.700 | [0.500, 0.900] | 20 |
| mrr | 0.502 | [0.327, 0.675] | 20 |
| ndcg@8 | 0.444 | [0.284, 0.601] | 20 |
| precision@8 | 0.113 | [0.075, 0.150] | 20 |
| recall@8 | 0.557 | [0.348, 0.750] | 20 |

## By category

### comparison

| metric | mean | 95% CI | n |
| --- | ---: | ---: | ---: |
| hit@1 | 0.500 | [0.000, 1.000] | 4 |
| hit@8 | 0.500 | [0.000, 1.000] | 4 |
| mrr | 0.500 | [0.000, 1.000] | 4 |
| ndcg@8 | 0.454 | [0.000, 0.909] | 4 |
| precision@8 | 0.125 | [0.000, 0.250] | 4 |
| recall@8 | 0.500 | [0.000, 1.000] | 4 |

### conceptual

| metric | mean | 95% CI | n |
| --- | ---: | ---: | ---: |
| hit@1 | 0.000 | [0.000, 0.000] | 4 |
| hit@8 | 0.750 | [0.250, 1.000] | 4 |
| mrr | 0.375 | [0.125, 0.500] | 4 |
| ndcg@8 | 0.406 | [0.151, 0.618] | 4 |
| precision@8 | 0.125 | [0.031, 0.219] | 4 |
| recall@8 | 0.625 | [0.250, 1.000] | 4 |

### exact_term

| metric | mean | 95% CI | n |
| --- | ---: | ---: | ---: |
| hit@1 | 0.000 | [0.000, 0.000] | 4 |
| hit@8 | 0.500 | [0.000, 1.000] | 4 |
| mrr | 0.250 | [0.000, 0.500] | 4 |
| ndcg@8 | 0.315 | [0.000, 0.631] | 4 |
| precision@8 | 0.062 | [0.000, 0.125] | 4 |
| recall@8 | 0.500 | [0.000, 1.000] | 4 |

### lookup

| metric | mean | 95% CI | n |
| --- | ---: | ---: | ---: |
| hit@1 | 0.500 | [0.000, 1.000] | 4 |
| hit@8 | 0.750 | [0.250, 1.000] | 4 |
| mrr | 0.583 | [0.167, 1.000] | 4 |
| ndcg@8 | 0.625 | [0.250, 1.000] | 4 |
| precision@8 | 0.094 | [0.031, 0.125] | 4 |
| recall@8 | 0.750 | [0.250, 1.000] | 4 |

### multi_hop

| metric | mean | 95% CI | n |
| --- | ---: | ---: | ---: |
| hit@1 | 0.750 | [0.250, 1.000] | 4 |
| hit@8 | 1.000 | [1.000, 1.000] | 4 |
| mrr | 0.800 | [0.400, 1.000] | 4 |
| ndcg@8 | 0.420 | [0.196, 0.682] | 4 |
| precision@8 | 0.156 | [0.125, 0.219] | 4 |
| recall@8 | 0.411 | [0.155, 0.792] | 4 |

### unanswerable

| metric | mean | 95% CI | n |
| --- | ---: | ---: | ---: |

## Worst 6 failures

### pilot-001 (exact_term, answerable)

**Question:** Does PEP 484 require Python to enforce type hints at runtime?

**Reference:** No. PEP 484 does not require runtime type checking.

**Retrieved sections:**

- ❌ [1] Type Hinting Generics In Standard Collections > Abstract (`e26e4b478a435481-0001`)
- ❌ [2] Protocols: Structural subtyping (static duck typing) > Abstract (`a35c304214b4044a-0001`)
- ❌ [3] Postponed Evaluation of Annotations > Rationale and Goals > Non-goals (`24cedd106580f3ea-0004`)
- ❌ [4] The Theory of Type Hints > Summary of gradual typing > Types vs. Classes (`00ed39463d0680a5-0010`)
- ❌ [5] TypedDict: Type Hints for Dictionaries with a Fixed Set of Keys > Specification (`2314151aef4c395d-0004`)
- ❌ [6] Type Hints > Rejected Alternatives > The problem of forward declarations (`a25e032f504686c8-0076`)
- ❌ [7] Deferred Evaluation Of Annotations Using Descriptors > Motivation > The Current State Of Annotation Use Cases > Static typing users (`ad23617867325d80-0013`)
- ❌ [8] Type Hints (`a25e032f504686c8-0000`)

**Metrics:** hit@1=0.00, hit@8=0.00, mrr=0.00, ndcg@8=0.00, precision@8=0.00, recall@8=0.00

### pilot-002 (exact_term, answerable)

**Question:** According to PEP 604, what does X | Y mean in a type annotation?

**Reference:** A union type, equivalent to Union[X, Y].

**Retrieved sections:**

- ❌ [1] Allow writing union types as ``X | Y`` > Motivation (`1b96f779896ff109-0002`)
- ❌ [2] Allow writing union types as ``X | Y`` > Objections and responses > 2. Change only PEP 484 (Type hints) to accept the syntax ``type1 | type2`` ? (`1b96f779896ff109-0010`)
- ❌ [3] Postponed Evaluation of Annotations > Abstract (`24cedd106580f3ea-0002`)
- ❌ [4] Type Hints > Type comments (`a25e032f504686c8-0047`)
- ❌ [5] Allow writing union types as ``X | Y`` (`1b96f779896ff109-0000`)
- ❌ [6] Flexible function and variable annotations > Motivation (`18ed3b62aa90c0eb-0002`)
- ❌ [7] Flexible function and variable annotations > Rationale (`18ed3b62aa90c0eb-0003`)
- ❌ [8] Deferred Evaluation Of Annotations Using Descriptors > Overview > Comparison Of Annotation Semantics (`ad23617867325d80-0006`)

**Metrics:** hit@1=0.00, hit@8=0.00, mrr=0.00, ndcg@8=0.00, precision@8=0.00, recall@8=0.00

### pilot-006 (lookup, answerable)

**Question:** Which methods form the context-manager protocol described by PEP 343?

**Reference:** The methods __enter__() and __exit__().

**Retrieved sections:**

- ❌ [1] The "with" Statement > Standard Terminology (`9b8996160cdfb03e-0019`)
- ❌ [2] The "with" Statement > Resolved Issues (`9b8996160cdfb03e-0022`)
- ❌ [3] The "with" Statement > References (`9b8996160cdfb03e-0034`)
- ❌ [4] Coroutines with async and await syntax > Specification > Asynchronous Context Managers and "async with" (`b6d5d84d24a46b97-0014`)
- ❌ [5] The "with" Statement > Reference Implementation (`9b8996160cdfb03e-0031`)
- ❌ [6] The "with" Statement > Caching Context Managers (`9b8996160cdfb03e-0020`)
- ❌ [7] The "with" Statement > Introduction (`9b8996160cdfb03e-0003`)
- ❌ [8] The "with" Statement > Examples (`9b8996160cdfb03e-0029`)

**Metrics:** hit@1=0.00, hit@8=0.00, mrr=0.00, ndcg@8=0.00, precision@8=0.00, recall@8=0.00

### pilot-012 (conceptual, answerable)

**Question:** Why does PEP 723 propose metadata inside standalone scripts?

**Reference:** So tools can discover a script's runtime requirements without a separate project file or tool-specific metadata format.

**Retrieved sections:**

- ❌ [1] Inline script metadata > Rejected Ideas > Why not use a comment block resembling requirements.txt? (`4ef54cafa35d2932-0022`)
- ❌ [2] Inline script metadata > Security Implications (`4ef54cafa35d2932-0011`)
- ❌ [3] Inline script metadata > Rejected Ideas > Why not reuse core metadata fields? (`4ef54cafa35d2932-0024`)
- ❌ [4] Inline script metadata > Rejected Ideas > Why not limit tool behavior? (`4ef54cafa35d2932-0027`)
- ❌ [5] Inline script metadata (`4ef54cafa35d2932-0000`)
- ❌ [6] Inline script metadata > Rationale (`4ef54cafa35d2932-0003`)
- ❌ [7] Inline script metadata > Rejected Ideas > Why not limit to specific metadata fields? (`4ef54cafa35d2932-0025`)
- ❌ [8] Inline script metadata > Abstract (`4ef54cafa35d2932-0001`)

**Metrics:** hit@1=0.00, hit@8=0.00, mrr=0.00, ndcg@8=0.00, precision@8=0.00, recall@8=0.00

### pilot-013 (comparison, answerable)

**Question:** What type-annotation features do PEP 585 and PEP 604 add?

**Reference:** PEP 585 adds generic parameter syntax to standard collections; PEP 604 adds X | Y syntax for union types.

**Retrieved sections:**

- ❌ [1] Allow writing union types as ``X | Y`` > Motivation (`1b96f779896ff109-0002`)
- ❌ [2] Flexible function and variable annotations > Motivation (`18ed3b62aa90c0eb-0002`)
- ❌ [3] Implementing PEP 649 > Deferred evaluation of PEP 695 and 696 objects (`80014392886f031e-0037`)
- ❌ [4] Implementing PEP 649 > Abstract (`80014392886f031e-0002`)
- ❌ [5] Flexible function and variable annotations > Abstract (`18ed3b62aa90c0eb-0001`)
- ❌ [6] Postponed Evaluation of Annotations > Rationale and Goals > Non-typing usage of annotations (`24cedd106580f3ea-0005`)
- ❌ [7] Style Guide for Python Code > Programming Recommendations > Function Annotations (`a55dfded40f487e1-0053`)
- ❌ [8] Type Hinting Generics In Standard Collections > Implementation (`e26e4b478a435481-0005`)

**Metrics:** hit@1=0.00, hit@8=0.00, mrr=0.00, ndcg@8=0.00, precision@8=0.00, recall@8=0.00

### pilot-015 (comparison, answerable)

**Question:** Where do PEP 621 and PEP 723 place metadata?

**Reference:** PEP 621 places project core metadata in pyproject.toml; PEP 723 embeds script metadata in the script itself.

**Retrieved sections:**

- ❌ [1] Storing project metadata in pyproject.toml (`74f7628b9d5e0341-0000`)
- ❌ [2] Storing project metadata in pyproject.toml > Rejected Ideas > Using structured TOML dictionaries to specify dependencies (`74f7628b9d5e0341-0043`)
- ❌ [3] Inline script metadata (`4ef54cafa35d2932-0000`)
- ❌ [4] Inline script metadata > Rejected Ideas > Why not use a comment block resembling requirements.txt? (`4ef54cafa35d2932-0022`)
- ❌ [5] Storing project metadata in pyproject.toml > Rejected Ideas > Support for a metadata provider (`74f7628b9d5e0341-0031`)
- ❌ [6] Version Identification and Dependency Specification > Version scheme > Version ordering across different metadata versions (`a5feae5ef825dc18-0035`)
- ❌ [7] Storing project metadata in pyproject.toml > Motivation (`74f7628b9d5e0341-0003`)
- ❌ [8] Storing project metadata in pyproject.toml > Specification (`74f7628b9d5e0341-0005`)

**Metrics:** hit@1=0.00, hit@8=0.00, mrr=0.00, ndcg@8=0.00, precision@8=0.00, recall@8=0.00
