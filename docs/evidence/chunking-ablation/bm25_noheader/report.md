# Eval run `20261005T072507Z_bm25_noheader`

- config: `bm25_noheader`
- created: 2026-10-05T07:25:16+00:00
- git: `3c0f709e850acfd9d02077570d942e76ca5fdf18` (dirty)
- dataset version: `0410ad782f35`
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
| hit@1 | 0.300 | [0.100, 0.500] | 20 |
| hit@8 | 0.650 | [0.450, 0.850] | 20 |
| mrr | 0.446 | [0.275, 0.629] | 20 |
| ndcg@8 | 0.391 | [0.232, 0.546] | 20 |
| precision@8 | 0.100 | [0.062, 0.131] | 20 |
| recall@8 | 0.465 | [0.282, 0.649] | 20 |

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
| hit@1 | 0.500 | [0.000, 1.000] | 4 |
| hit@8 | 1.000 | [1.000, 1.000] | 4 |
| mrr | 0.750 | [0.500, 1.000] | 4 |
| ndcg@8 | 0.712 | [0.498, 0.916] | 4 |
| precision@8 | 0.156 | [0.125, 0.219] | 4 |
| recall@8 | 0.875 | [0.625, 1.000] | 4 |

### exact_term

| metric | mean | 95% CI | n |
| --- | ---: | ---: | ---: |
| hit@1 | 0.000 | [0.000, 0.000] | 4 |
| hit@8 | 0.000 | [0.000, 0.000] | 4 |
| mrr | 0.000 | [0.000, 0.000] | 4 |
| ndcg@8 | 0.000 | [0.000, 0.000] | 4 |
| precision@8 | 0.000 | [0.000, 0.000] | 4 |
| recall@8 | 0.000 | [0.000, 0.000] | 4 |

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
| mrr | 0.542 | [0.333, 0.833] | 4 |
| ndcg@8 | 0.322 | [0.204, 0.519] | 4 |
| precision@8 | 0.156 | [0.125, 0.219] | 4 |
| recall@8 | 0.327 | [0.232, 0.458] | 4 |

### unanswerable

| metric | mean | 95% CI | n |
| --- | ---: | ---: | ---: |

## Worst 7 failures

### pilot-001 (exact_term, answerable)

**Question:** Does PEP 484 require Python to enforce type hints at runtime?

**Reference:** No. PEP 484 does not require runtime type checking.

**Retrieved sections:**

- ❌ [1] Deferred Evaluation Of Annotations Using Descriptors > Motivation > The Current State Of Annotation Use Cases > Static typing users (`ad23617867325d80-0013`)
- ❌ [2] Postponed Evaluation of Annotations > Rationale and Goals > Non-goals (`24cedd106580f3ea-0004`)
- ❌ [3] Protocols: Structural subtyping (static duck typing) > Abstract (`a35c304214b4044a-0001`)
- ❌ [4] Allow writing union types as ``X | Y`` > Motivation (`1b96f779896ff109-0002`)
- ❌ [5] Type Hints > Rejected Alternatives > The double colon (`a25e032f504686c8-0078`)
- ❌ [6] Syntax for Variable Annotations > Rationale > Non-goals (`4e9bac3fbbd66adf-0005`)
- ❌ [7] Type Hints > Rejected Alternatives > The double colon (`a25e032f504686c8-0077`)
- ❌ [8] Deferred Evaluation Of Annotations Using Descriptors > Motivation > The Current State Of Annotation Use Cases > Documentation (`ad23617867325d80-0017`)

**Metrics:** hit@1=0.00, hit@8=0.00, mrr=0.00, ndcg@8=0.00, precision@8=0.00, recall@8=0.00

### pilot-002 (exact_term, answerable)

**Question:** According to PEP 604, what does X | Y mean in a type annotation?

**Reference:** A union type, equivalent to Union[X, Y].

**Retrieved sections:**

- ❌ [1] Syntax for Variable Annotations > Rejected/Postponed Proposals (`4e9bac3fbbd66adf-0020`)
- ❌ [2] Allow writing union types as ``X | Y`` > Motivation (`1b96f779896ff109-0002`)
- ❌ [3] Syntax for Variable Annotations > Specification > Annotating expressions (`4e9bac3fbbd66adf-0011`)
- ❌ [4] Deferred Evaluation Of Annotations Using Descriptors > Overview > Comparison Of Annotation Semantics (`ad23617867325d80-0005`)
- ❌ [5] Literal Types > Legal and illegal parameterizations > Parameters at runtime (`e37217a67ced11bb-0013`)
- ❌ [6] None-aware operators > Rejected Ideas > ``?`` Unary Postfix Operator (`d8b65ec94c20dcc6-0028`)
- ❌ [7] Assignment Expressions > Rejected alternative proposals > Alternative spellings (`94c93f7fd8babcee-0028`)
- ❌ [8] Deferred Evaluation Of Annotations Using Descriptors > Overview > Comparison Of Annotation Semantics (`ad23617867325d80-0007`)

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
- ❌ [3] Type Parameter Syntax > Specification > Type Parameter Scopes (`62b2ba99b0d1350a-0020`)
- ❌ [4] Syntax for Variable Annotations > Specification (`4e9bac3fbbd66adf-0006`)
- ❌ [5] Annotating Type Forms > Specification > Valid Type Expressions (`cedb11e7569c13e5-0011`)
- ❌ [6] Assignment Expressions > Syntax and semantics > Scope of the target (`94c93f7fd8babcee-0009`)
- ❌ [7] None-aware operators > Rejected Ideas > Exception-aware operators (`d8b65ec94c20dcc6-0024`)
- ❌ [8] Deferred Evaluation Of Annotations Using Descriptors > Motivation > A History Of Annotations (`ad23617867325d80-0009`)

**Metrics:** hit@1=0.00, hit@8=0.00, mrr=0.00, ndcg@8=0.00, precision@8=0.00, recall@8=0.00

### pilot-006 (lookup, answerable)

**Question:** Which methods form the context-manager protocol described by PEP 343?

**Reference:** The methods __enter__() and __exit__().

**Retrieved sections:**

- ❌ [1] The "with" Statement > Standard Terminology (`9b8996160cdfb03e-0019`)
- ❌ [2] Coroutines with async and await syntax > Specification > Asynchronous Context Managers and "async with" (`b6d5d84d24a46b97-0014`)
- ❌ [3] The "with" Statement > References (`9b8996160cdfb03e-0034`)
- ❌ [4] The "with" Statement > Resolved Issues (`9b8996160cdfb03e-0022`)
- ❌ [5] The "with" Statement > Caching Context Managers (`9b8996160cdfb03e-0020`)
- ❌ [6] Coroutines with async and await syntax > Glossary (`b6d5d84d24a46b97-0029`)
- ❌ [7] The "with" Statement > Examples (`9b8996160cdfb03e-0030`)
- ❌ [8] The "with" Statement > Examples (`9b8996160cdfb03e-0029`)

**Metrics:** hit@1=0.00, hit@8=0.00, mrr=0.00, ndcg@8=0.00, precision@8=0.00, recall@8=0.00

### pilot-013 (comparison, answerable)

**Question:** What type-annotation features do PEP 585 and PEP 604 add?

**Reference:** PEP 585 adds generic parameter syntax to standard collections; PEP 604 adds X | Y syntax for union types.

**Retrieved sections:**

- ❌ [1] Allow writing union types as ``X | Y`` > Motivation (`1b96f779896ff109-0002`)
- ❌ [2] Type Hinting Generics In Standard Collections > Implementation (`e26e4b478a435481-0005`)
- ❌ [3] Inline script metadata > Rejected Ideas > Why not use a comment block resembling requirements.txt? (`4ef54cafa35d2932-0022`)
- ❌ [4] Implementing PEP 649 > Abstract (`80014392886f031e-0002`)
- ❌ [5] Marking individual TypedDict items as required or potentially-missing > Rejected Ideas > Replace Optional with Nullable. Repurpose Optional to mean “optional item”. (`96c61294f2cd86dd-0022`)
- ❌ [6] Type Hinting Generics In Standard Collections (`e26e4b478a435481-0000`)
- ❌ [7] TypedDict: Type Hints for Dictionaries with a Fixed Set of Keys > Rejected Alternatives (`2314151aef4c395d-0021`)
- ❌ [8] Data Class Transforms > Rationale (`d19a07254ec82051-0003`)

**Metrics:** hit@1=0.00, hit@8=0.00, mrr=0.00, ndcg@8=0.00, precision@8=0.00, recall@8=0.00

### pilot-015 (comparison, answerable)

**Question:** Where do PEP 621 and PEP 723 place metadata?

**Reference:** PEP 621 places project core metadata in pyproject.toml; PEP 723 embeds script metadata in the script itself.

**Retrieved sections:**

- ❌ [1] Storing project metadata in pyproject.toml (`74f7628b9d5e0341-0000`)
- ❌ [2] Inline script metadata > Security Implications (`4ef54cafa35d2932-0011`)
- ❌ [3] Dependency Groups in pyproject.toml > Deferred Ideas > Why not support Dependency Group Includes in ``[project.dependencies]`` or ``[project.optional-dependencies]``? (`291eff3d2334240d-0034`)
- ❌ [4] Storing project metadata in pyproject.toml > Rejected Ideas > Drop ``maintainers`` to unify with ``authors`` (`74f7628b9d5e0341-0041`)
- ❌ [5] Storing project metadata in pyproject.toml > Rejected Ideas > Support for a metadata provider (`74f7628b9d5e0341-0031`)
- ❌ [6] Inline script metadata (`4ef54cafa35d2932-0000`)
- ❌ [7] Dependency specification for Python Software Packages > Specification > Environment Markers (`c16921c303e8286b-0013`)
- ❌ [8] Inline script metadata > Specification (`4ef54cafa35d2932-0005`)

**Metrics:** hit@1=0.00, hit@8=0.00, mrr=0.00, ndcg@8=0.00, precision@8=0.00, recall@8=0.00
