# Eval run `20261005T030406Z_bm25_only`

- config: `bm25_only`
- created: 2026-10-05T03:04:09+00:00
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
| hit@1 | 0.250 | [0.100, 0.450] | 20 |
| hit@8 | 0.700 | [0.500, 0.900] | 20 |
| mrr | 0.420 | [0.257, 0.592] | 20 |
| ndcg@8 | 0.380 | [0.231, 0.523] | 20 |
| precision@8 | 0.106 | [0.075, 0.144] | 20 |
| recall@8 | 0.490 | [0.315, 0.657] | 20 |

## By category

### comparison

| metric | mean | 95% CI | n |
| --- | ---: | ---: | ---: |
| hit@1 | 0.500 | [0.000, 1.000] | 4 |
| hit@8 | 0.500 | [0.000, 1.000] | 4 |
| mrr | 0.500 | [0.000, 1.000] | 4 |
| ndcg@8 | 0.403 | [0.000, 0.807] | 4 |
| precision@8 | 0.094 | [0.000, 0.188] | 4 |
| recall@8 | 0.375 | [0.000, 0.750] | 4 |

### conceptual

| metric | mean | 95% CI | n |
| --- | ---: | ---: | ---: |
| hit@1 | 0.250 | [0.000, 0.750] | 4 |
| hit@8 | 1.000 | [1.000, 1.000] | 4 |
| mrr | 0.625 | [0.500, 0.875] | 4 |
| ndcg@8 | 0.620 | [0.448, 0.731] | 4 |
| precision@8 | 0.156 | [0.125, 0.219] | 4 |
| recall@8 | 0.875 | [0.625, 1.000] | 4 |

### exact_term

| metric | mean | 95% CI | n |
| --- | ---: | ---: | ---: |
| hit@1 | 0.000 | [0.000, 0.000] | 4 |
| hit@8 | 0.250 | [0.000, 0.750] | 4 |
| mrr | 0.036 | [0.000, 0.107] | 4 |
| ndcg@8 | 0.051 | [0.000, 0.153] | 4 |
| precision@8 | 0.031 | [0.000, 0.094] | 4 |
| recall@8 | 0.125 | [0.000, 0.375] | 4 |

### lookup

| metric | mean | 95% CI | n |
| --- | ---: | ---: | ---: |
| hit@1 | 0.250 | [0.000, 0.750] | 4 |
| hit@8 | 0.750 | [0.250, 1.000] | 4 |
| mrr | 0.438 | [0.125, 0.750] | 4 |
| ndcg@8 | 0.515 | [0.158, 0.815] | 4 |
| precision@8 | 0.094 | [0.031, 0.125] | 4 |
| recall@8 | 0.750 | [0.250, 1.000] | 4 |

### multi_hop

| metric | mean | 95% CI | n |
| --- | ---: | ---: | ---: |
| hit@1 | 0.250 | [0.000, 0.750] | 4 |
| hit@8 | 1.000 | [1.000, 1.000] | 4 |
| mrr | 0.500 | [0.333, 0.833] | 4 |
| ndcg@8 | 0.308 | [0.186, 0.519] | 4 |
| precision@8 | 0.156 | [0.125, 0.219] | 4 |
| recall@8 | 0.327 | [0.232, 0.458] | 4 |

### unanswerable

| metric | mean | 95% CI | n |
| --- | ---: | ---: | ---: |

## Worst 6 failures

### pilot-002 (exact_term, answerable)

**Question:** According to PEP 604, what does X | Y mean in a type annotation?

**Reference:** A union type, equivalent to Union[X, Y].

**Retrieved sections:**

- ❌ [1] Syntax for Variable Annotations > Rejected/Postponed Proposals (`4e9bac3fbbd66adf-0020`)
- ❌ [2] Allow writing union types as ``X | Y`` > Motivation (`1b96f779896ff109-0002`)
- ❌ [3] Marking individual TypedDict items as required or potentially-missing > Rejected Ideas > Replace Optional with Nullable. Repurpose Optional to mean “optional item”. (`96c61294f2cd86dd-0022`)
- ❌ [4] Deferred Evaluation Of Annotations Using Descriptors > Overview > Comparison Of Annotation Semantics (`ad23617867325d80-0005`)
- ❌ [5] Syntax for Variable Annotations > Specification > Annotating expressions (`4e9bac3fbbd66adf-0011`)
- ❌ [6] Deferred Evaluation Of Annotations Using Descriptors > Overview > Comparison Of Annotation Semantics (`ad23617867325d80-0007`)
- ❌ [7] Literal Types > Legal and illegal parameterizations > Parameters at runtime (`e37217a67ced11bb-0013`)
- ❌ [8] Assignment Expressions > Rejected alternative proposals > Alternative spellings (`94c93f7fd8babcee-0028`)

**Metrics:** hit@1=0.00, hit@8=0.00, mrr=0.00, ndcg@8=0.00, precision@8=0.00, recall@8=0.00

### pilot-003 (exact_term, answerable)

**Question:** According to PEP 655, what do Required[] and NotRequired[] mean for a TypedDict key?

**Reference:** Required[] means the key must be present; NotRequired[] means it may be absent.

**Retrieved sections:**

- ❌ [1] Using TypedDict for more precise \*\*kwargs typing > Specification > Required and non-required keys (`676be8f1d20eb181-0009`)
- ❌ [2] Marking individual TypedDict items as required or potentially-missing > Specification (`96c61294f2cd86dd-0004`)
- ❌ [3] TypedDict: Read-only items > Specification > Type consistency (`8b8ef45a4e81715d-0013`)
- ❌ [4] Marking individual TypedDict items as required or potentially-missing > How to Teach This (`96c61294f2cd86dd-0011`)
- ❌ [5] TypedDict: Read-only items > Specification > Interaction with other special types (`8b8ef45a4e81715d-0011`)
- ❌ [6] Marking individual TypedDict items as required or potentially-missing > Motivation (`96c61294f2cd86dd-0002`)
- ❌ [7] Marking individual TypedDict items as required or potentially-missing > Rejected Ideas > Marking required or potentially-missing keys with an operator (`96c61294f2cd86dd-0015`)
- ❌ [8] TypedDict: Read-only items > Specification > Type consistency (`8b8ef45a4e81715d-0014`)

**Metrics:** hit@1=0.00, hit@8=0.00, mrr=0.00, ndcg@8=0.00, precision@8=0.00, recall@8=0.00

### pilot-004 (exact_term, answerable)

**Question:** What syntax does PEP 572 introduce for assigning a value within an expression?

**Reference:** NAME := expr.

**Retrieved sections:**

- ❌ [1] Structural Pattern Matching: Specification > Syntax and Semantics > Patterns > Capture Patterns (`efde821a3005f52a-0012`)
- ❌ [2] Syntax for Variable Annotations > Rejected/Postponed Proposals (`4e9bac3fbbd66adf-0019`)
- ❌ [3] Syntax for Variable Annotations > Specification (`4e9bac3fbbd66adf-0006`)
- ❌ [4] Type Parameter Syntax > Specification > Type Parameter Scopes (`62b2ba99b0d1350a-0020`)
- ❌ [5] Assignment Expressions > Syntax and semantics > Scope of the target (`94c93f7fd8babcee-0009`)
- ❌ [6] Annotating Type Forms > Specification > Valid Type Expressions (`cedb11e7569c13e5-0011`)
- ❌ [7] None-aware operators > Rejected Ideas > Exception-aware operators (`d8b65ec94c20dcc6-0024`)
- ❌ [8] Type Parameter Syntax > Specification > Generic Type Alias (`62b2ba99b0d1350a-0012`)

**Metrics:** hit@1=0.00, hit@8=0.00, mrr=0.00, ndcg@8=0.00, precision@8=0.00, recall@8=0.00

### pilot-006 (lookup, answerable)

**Question:** Which methods form the context-manager protocol described by PEP 343?

**Reference:** The methods __enter__() and __exit__().

**Retrieved sections:**

- ❌ [1] The "with" Statement > Standard Terminology (`9b8996160cdfb03e-0019`)
- ❌ [2] Coroutines with async and await syntax > Specification > Asynchronous Context Managers and "async with" (`b6d5d84d24a46b97-0014`)
- ❌ [3] The "with" Statement > References (`9b8996160cdfb03e-0034`)
- ❌ [4] The "with" Statement > Caching Context Managers (`9b8996160cdfb03e-0020`)
- ❌ [5] The "with" Statement > Resolved Issues (`9b8996160cdfb03e-0022`)
- ❌ [6] The "with" Statement > Examples (`9b8996160cdfb03e-0030`)
- ❌ [7] Coroutines with async and await syntax > Glossary (`b6d5d84d24a46b97-0029`)
- ❌ [8] The "with" Statement > Examples (`9b8996160cdfb03e-0029`)

**Metrics:** hit@1=0.00, hit@8=0.00, mrr=0.00, ndcg@8=0.00, precision@8=0.00, recall@8=0.00

### pilot-013 (comparison, answerable)

**Question:** What type-annotation features do PEP 585 and PEP 604 add?

**Reference:** PEP 585 adds generic parameter syntax to standard collections; PEP 604 adds X | Y syntax for union types.

**Retrieved sections:**

- ❌ [1] Allow writing union types as ``X | Y`` > Motivation (`1b96f779896ff109-0002`)
- ❌ [2] Type Hinting Generics In Standard Collections > Implementation (`e26e4b478a435481-0005`)
- ❌ [3] Inline script metadata > Rejected Ideas > Why not use a comment block resembling requirements.txt? (`4ef54cafa35d2932-0022`)
- ❌ [4] Deferred Evaluation Of Annotations Using Descriptors > Motivation > The Current State Of Annotation Use Cases > Static typing users (`ad23617867325d80-0013`)
- ❌ [5] Implementing PEP 649 > Abstract (`80014392886f031e-0002`)
- ❌ [6] Add Union Operators To dict > Major Objections > What About The Full ``set`` API? > Response (`906a0793c28adfc4-0023`)
- ❌ [7] Type Hinting Generics In Standard Collections (`e26e4b478a435481-0000`)
- ❌ [8] Deferred Evaluation Of Annotations Using Descriptors > Overview > Comparison Of Annotation Semantics (`ad23617867325d80-0007`)

**Metrics:** hit@1=0.00, hit@8=0.00, mrr=0.00, ndcg@8=0.00, precision@8=0.00, recall@8=0.00

### pilot-015 (comparison, answerable)

**Question:** Where do PEP 621 and PEP 723 place metadata?

**Reference:** PEP 621 places project core metadata in pyproject.toml; PEP 723 embeds script metadata in the script itself.

**Retrieved sections:**

- ❌ [1] Storing project metadata in pyproject.toml (`74f7628b9d5e0341-0000`)
- ❌ [2] Inline script metadata > Security Implications (`4ef54cafa35d2932-0011`)
- ❌ [3] Dependency Groups in pyproject.toml > Deferred Ideas > Why not support Dependency Group Includes in ``[project.dependencies]`` or ``[project.optional-dependencies]``? (`291eff3d2334240d-0034`)
- ❌ [4] Storing project metadata in pyproject.toml > Rejected Ideas > Drop ``maintainers`` to unify with ``authors`` (`74f7628b9d5e0341-0041`)
- ❌ [5] Inline script metadata (`4ef54cafa35d2932-0000`)
- ❌ [6] Storing project metadata in pyproject.toml > Rejected Ideas > Support for a metadata provider (`74f7628b9d5e0341-0031`)
- ❌ [7] Inline script metadata > Specification (`4ef54cafa35d2932-0005`)
- ❌ [8] Dependency specification for Python Software Packages > Specification > Environment Markers (`c16921c303e8286b-0013`)

**Metrics:** hit@1=0.00, hit@8=0.00, mrr=0.00, ndcg@8=0.00, precision@8=0.00, recall@8=0.00
