# Eval run `20261005T072446Z_bm25_tokens250`

- config: `bm25_tokens250`
- created: 2026-10-05T07:24:58+00:00
- git: `3c0f709e850acfd9d02077570d942e76ca5fdf18` (dirty)
- dataset version: `962bbf10fec4`
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
| hit@8 | 0.600 | [0.400, 0.800] | 20 |
| mrr | 0.458 | [0.263, 0.654] | 20 |
| ndcg@8 | 0.356 | [0.203, 0.508] | 20 |
| precision@8 | 0.100 | [0.062, 0.138] | 20 |
| recall@8 | 0.387 | [0.220, 0.563] | 20 |

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
| hit@1 | 0.750 | [0.250, 1.000] | 4 |
| hit@8 | 1.000 | [1.000, 1.000] | 4 |
| mrr | 0.833 | [0.500, 1.000] | 4 |
| ndcg@8 | 0.568 | [0.505, 0.615] | 4 |
| precision@8 | 0.188 | [0.125, 0.250] | 4 |
| recall@8 | 0.625 | [0.417, 0.875] | 4 |

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
| hit@1 | 0.500 | [0.000, 1.000] | 4 |
| hit@8 | 0.750 | [0.250, 1.000] | 4 |
| mrr | 0.562 | [0.125, 1.000] | 4 |
| ndcg@8 | 0.608 | [0.215, 1.000] | 4 |
| precision@8 | 0.094 | [0.031, 0.125] | 4 |
| recall@8 | 0.750 | [0.250, 1.000] | 4 |

### multi_hop

| metric | mean | 95% CI | n |
| --- | ---: | ---: | ---: |
| hit@1 | 0.250 | [0.000, 0.750] | 4 |
| hit@8 | 0.750 | [0.250, 1.000] | 4 |
| mrr | 0.396 | [0.083, 0.812] | 4 |
| ndcg@8 | 0.201 | [0.054, 0.379] | 4 |
| precision@8 | 0.125 | [0.031, 0.219] | 4 |
| recall@8 | 0.186 | [0.062, 0.310] | 4 |

### unanswerable

| metric | mean | 95% CI | n |
| --- | ---: | ---: | ---: |

## Worst 8 failures

### pilot-001 (exact_term, answerable)

**Question:** Does PEP 484 require Python to enforce type hints at runtime?

**Reference:** No. PEP 484 does not require runtime type checking.

**Retrieved sections:**

- ❌ [1] Allow writing union types as ``X | Y`` > Motivation (`1b96f779896ff109-0002`)
- ❌ [2] Syntax for Variable Annotations > Specification (`4e9bac3fbbd66adf-0008`)
- ❌ [3] Postponed Evaluation of Annotations > Rationale and Goals > Non-goals (`24cedd106580f3ea-0004`)
- ❌ [4] Marking individual TypedDict items as required or potentially-missing > Specification (`96c61294f2cd86dd-0007`)
- ❌ [5] Protocols: Structural subtyping (static duck typing) > Abstract (`a35c304214b4044a-0001`)
- ❌ [6] Syntax for Variable Annotations > Rationale > Non-goals (`4e9bac3fbbd66adf-0007`)
- ❌ [7] Deferred Evaluation Of Annotations Using Descriptors > Motivation > The Current State Of Annotation Use Cases > Static typing users (`ad23617867325d80-0022`)
- ❌ [8] Protocols: Structural subtyping (static duck typing) > Rationale and Goals > Non-goals (`a35c304214b4044a-0006`)

**Metrics:** hit@1=0.00, hit@8=0.00, mrr=0.00, ndcg@8=0.00, precision@8=0.00, recall@8=0.00

### pilot-002 (exact_term, answerable)

**Question:** According to PEP 604, what does X | Y mean in a type annotation?

**Reference:** A union type, equivalent to Union[X, Y].

**Retrieved sections:**

- ❌ [1] Syntax for Variable Annotations > Rejected/Postponed Proposals (`4e9bac3fbbd66adf-0027`)
- ❌ [2] Allow writing union types as ``X | Y`` > Motivation (`1b96f779896ff109-0002`)
- ❌ [3] Syntax for Variable Annotations > Rejected/Postponed Proposals (`4e9bac3fbbd66adf-0026`)
- ❌ [4] Marking individual TypedDict items as required or potentially-missing > Rejected Ideas > Replace Optional with Nullable. Repurpose Optional to mean “optional item”. (`96c61294f2cd86dd-0029`)
- ❌ [5] Syntax for Variable Annotations > Specification > Annotating expressions (`4e9bac3fbbd66adf-0015`)
- ❌ [6] Assignment Expressions > Rejected alternative proposals > Alternative spellings (`94c93f7fd8babcee-0037`)
- ❌ [7] Deferred Evaluation Of Annotations Using Descriptors > Overview > Comparison Of Annotation Semantics (`ad23617867325d80-0008`)
- ❌ [8] Type Hints > Type comments (`a25e032f504686c8-0068`)

**Metrics:** hit@1=0.00, hit@8=0.00, mrr=0.00, ndcg@8=0.00, precision@8=0.00, recall@8=0.00

### pilot-003 (exact_term, answerable)

**Question:** According to PEP 655, what do Required[] and NotRequired[] mean for a TypedDict key?

**Reference:** Required[] means the key must be present; NotRequired[] means it may be absent.

**Retrieved sections:**

- ❌ [1] Using TypedDict for more precise \*\*kwargs typing > Specification > Required and non-required keys (`676be8f1d20eb181-0011`)
- ❌ [2] Marking individual TypedDict items as required or potentially-missing > Specification (`96c61294f2cd86dd-0006`)
- ❌ [3] TypedDict: Read-only items > Specification > Interaction with other special types (`8b8ef45a4e81715d-0015`)
- ❌ [4] Marking individual TypedDict items as required or potentially-missing > Motivation (`96c61294f2cd86dd-0002`)
- ❌ [5] Marking individual TypedDict items as required or potentially-missing > Rejected Ideas > Marking required or potentially-missing keys with an operator (`96c61294f2cd86dd-0020`)
- ❌ [6] TypedDict: Read-only items > Specification > Type consistency (`8b8ef45a4e81715d-0019`)
- ❌ [7] Marking individual TypedDict items as required or potentially-missing > How to Teach This (`96c61294f2cd86dd-0014`)
- ❌ [8] Marking individual TypedDict items as required or potentially-missing > Specification (`96c61294f2cd86dd-0007`)

**Metrics:** hit@1=0.00, hit@8=0.00, mrr=0.00, ndcg@8=0.00, precision@8=0.00, recall@8=0.00

### pilot-004 (exact_term, answerable)

**Question:** What syntax does PEP 572 introduce for assigning a value within an expression?

**Reference:** NAME := expr.

**Retrieved sections:**

- ❌ [1] Structural Pattern Matching: Specification > Syntax and Semantics > Patterns > Capture Patterns (`efde821a3005f52a-0015`)
- ❌ [2] Syntax for Variable Annotations > Specification (`4e9bac3fbbd66adf-0008`)
- ❌ [3] Type Parameter Syntax > Specification > Type Parameter Scopes (`62b2ba99b0d1350a-0028`)
- ❌ [4] Assignment Expressions > Syntax and semantics > Scope of the target (`94c93f7fd8babcee-0011`)
- ❌ [5] Syntax for Variable Annotations > Rejected/Postponed Proposals (`4e9bac3fbbd66adf-0025`)
- ❌ [6] Annotating Type Forms > Specification > Valid Type Expressions (`cedb11e7569c13e5-0015`)
- ❌ [7] Data Classes > Specification (`cb84384cb5f17589-0016`)
- ❌ [8] Type Parameter Syntax > Specification > Type Parameter Scopes (`62b2ba99b0d1350a-0027`)

**Metrics:** hit@1=0.00, hit@8=0.00, mrr=0.00, ndcg@8=0.00, precision@8=0.00, recall@8=0.00

### pilot-006 (lookup, answerable)

**Question:** Which methods form the context-manager protocol described by PEP 343?

**Reference:** The methods __enter__() and __exit__().

**Retrieved sections:**

- ❌ [1] Coroutines with async and await syntax > Specification > Asynchronous Context Managers and "async with" (`b6d5d84d24a46b97-0021`)
- ❌ [2] The "with" Statement > Standard Terminology (`9b8996160cdfb03e-0028`)
- ❌ [3] The "with" Statement > References (`9b8996160cdfb03e-0053`)
- ❌ [4] The "with" Statement > Standard Terminology (`9b8996160cdfb03e-0029`)
- ❌ [5] The "with" Statement > Caching Context Managers (`9b8996160cdfb03e-0031`)
- ❌ [6] The "with" Statement > Caching Context Managers (`9b8996160cdfb03e-0030`)
- ❌ [7] Coroutines with async and await syntax > Glossary (`b6d5d84d24a46b97-0040`)
- ❌ [8] The "with" Statement > Resolved Issues (`9b8996160cdfb03e-0033`)

**Metrics:** hit@1=0.00, hit@8=0.00, mrr=0.00, ndcg@8=0.00, precision@8=0.00, recall@8=0.00

### pilot-013 (comparison, answerable)

**Question:** What type-annotation features do PEP 585 and PEP 604 add?

**Reference:** PEP 585 adds generic parameter syntax to standard collections; PEP 604 adds X | Y syntax for union types.

**Retrieved sections:**

- ❌ [1] Allow writing union types as ``X | Y`` > Motivation (`1b96f779896ff109-0002`)
- ❌ [2] Type Hinting Generics In Standard Collections > Implementation (`e26e4b478a435481-0005`)
- ❌ [3] Inline script metadata > Rejected Ideas > Why not use a comment block resembling requirements.txt? (`4ef54cafa35d2932-0030`)
- ❌ [4] Deferred Evaluation Of Annotations Using Descriptors > Motivation > The Current State Of Annotation Use Cases > Static typing users (`ad23617867325d80-0022`)
- ❌ [5] Implementing PEP 649 > Abstract (`80014392886f031e-0002`)
- ❌ [6] Add Union Operators To dict > Major Objections > What About The Full ``set`` API? > Response (`906a0793c28adfc4-0028`)
- ❌ [7] Type Hinting Generics In Standard Collections (`e26e4b478a435481-0000`)
- ❌ [8] Flexible function and variable annotations > Motivation (`18ed3b62aa90c0eb-0002`)

**Metrics:** hit@1=0.00, hit@8=0.00, mrr=0.00, ndcg@8=0.00, precision@8=0.00, recall@8=0.00

### pilot-015 (comparison, answerable)

**Question:** Where do PEP 621 and PEP 723 place metadata?

**Reference:** PEP 621 places project core metadata in pyproject.toml; PEP 723 embeds script metadata in the script itself.

**Retrieved sections:**

- ❌ [1] Storing project metadata in pyproject.toml (`74f7628b9d5e0341-0000`)
- ❌ [2] Dependency Groups in pyproject.toml > Deferred Ideas > Why not support Dependency Group Includes in ``[project.dependencies]`` or ``[project.optional-dependencies]``? (`291eff3d2334240d-0045`)
- ❌ [3] Inline script metadata > Security Implications (`4ef54cafa35d2932-0016`)
- ❌ [4] Storing project metadata in pyproject.toml > Rejected Ideas > Drop ``maintainers`` to unify with ``authors`` (`74f7628b9d5e0341-0047`)
- ❌ [5] Storing project metadata in pyproject.toml > Rejected Ideas > Support for a metadata provider (`74f7628b9d5e0341-0037`)
- ❌ [6] Inline script metadata > Specification (`4ef54cafa35d2932-0008`)
- ❌ [7] Inline script metadata (`4ef54cafa35d2932-0000`)
- ❌ [8] Version Identification and Dependency Specification > Definitions (`a5feae5ef825dc18-0003`)

**Metrics:** hit@1=0.00, hit@8=0.00, mrr=0.00, ndcg@8=0.00, precision@8=0.00, recall@8=0.00

### pilot-020 (multi_hop, answerable)

**Question:** Which type-hinting PEP does PEP 544 extend, and does that earlier proposal require runtime type checking?

**Reference:** PEP 484. It does not require runtime type checking.

**Retrieved sections:**

- ❌ [1] Syntax for Variable Annotations > Rationale > Non-goals (`4e9bac3fbbd66adf-0007`)
- ❌ [2] Postponed Evaluation of Annotations > Rationale and Goals > Non-typing usage of annotations (`24cedd106580f3ea-0005`)
- ❌ [3] Type Hinting Generics In Standard Collections > Rejected alternatives > Making ``isinstance(obj, list[str])`` perform a runtime type check (`e26e4b478a435481-0019`)
- ❌ [4] Arbitrary Literal String Type > Rejected Alternatives > Runtime Checkable ``LiteralString`` (`037f79d0f8ba9656-0037`)
- ❌ [5] Protocols: Structural subtyping (static duck typing) > Existing Approaches to Structural Subtyping (`a35c304214b4044a-0012`)
- ❌ [6] Type Hints > Compatibility with other uses of function annotations (`a25e032f504686c8-0065`)
- ❌ [7] Type Hinting Generics In Standard Collections > Abstract (`e26e4b478a435481-0001`)
- ❌ [8] Type Hints > Rationale and Goals (`a25e032f504686c8-0004`)

**Metrics:** hit@1=0.00, hit@8=0.00, mrr=0.00, ndcg@8=0.00, precision@8=0.00, recall@8=0.00
