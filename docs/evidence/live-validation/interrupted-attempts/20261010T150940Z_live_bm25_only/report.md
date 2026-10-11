# Eval run `20261010T150940Z_live_bm25_only`

- config: `live_bm25_only`
- created: 2026-10-10T15:11:12+00:00
- git: `c1193279bda76c5d2ca549e84668607de824a111` (dirty)
- dataset version: `27b46e65f45d`
- eval set: `v1` @ `1f48f2e04ef7` (24 items)
- prompts: {'answer': 'answer_v1', 'judge_faithfulness': 'judge_faithfulness_v1', 'judge_correctness': 'judge_correctness_v1', 'judge_relevance': 'judge_relevance_v1'}
- generator: `claude-sonnet-5`  judge: `claude-haiku-4-5`  provider: `cached(budgeted(anthropic))`
- retrieval only: False
- LLM calls: 52 (cache hits 13, misses 39); tokens in/out: 76447/7930; estimated cost: n/a
- errors: 13; items whose labels matched no chunk: 0
- bootstrap: 1000 resamples, seed 0

## Usage accounting

Token totals include cached responses; incremental cost excludes cache hits. Rates are applied separately per requested model. Hidden SDK retries and provider billing adjustments are not independently observable.

Calls with unknown usage: 13

| Model | Total input | Total output | Billable input | Billable output |
| --- | ---: | ---: | ---: | ---: |
| claude-haiku-4-5 | 32796 | 5513 | 21506 | 3550 |
| claude-sonnet-5 | 43651 | 2417 | 28881 | 1548 |

## Metrics

| metric | mean | 95% CI | n |
| --- | ---: | ---: | ---: |
| abstained | 0.167 | [0.000, 0.417] | 12 |
| answered_without_citations | 0.000 | [0.000, 0.000] | 10 |
| citations_valid | 1.000 | [1.000, 1.000] | 10 |
| correct_abstention | 1.000 | [1.000, 1.000] | 1 |
| correctness | 0.900 | [0.700, 1.000] | 10 |
| faithfulness | 0.944 | [0.833, 1.000] | 9 |
| hit@1 | 0.250 | [0.100, 0.450] | 20 |
| hit@8 | 0.700 | [0.500, 0.900] | 20 |
| missed_abstention | 0.000 | [0.000, 0.000] | 1 |
| mrr | 0.420 | [0.257, 0.592] | 20 |
| ndcg@8 | 0.380 | [0.231, 0.523] | 20 |
| precision@8 | 0.106 | [0.075, 0.144] | 20 |
| recall@8 | 0.490 | [0.315, 0.657] | 20 |
| relevance | 1.000 | [1.000, 1.000] | 9 |
| unnecessary_abstention | 0.091 | [0.000, 0.273] | 11 |

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
| abstained | 0.000 | [0.000, 0.000] | 2 |
| answered_without_citations | 0.000 | [0.000, 0.000] | 2 |
| citations_valid | 1.000 | [1.000, 1.000] | 2 |
| correctness | 1.000 | [1.000, 1.000] | 1 |
| faithfulness | 1.000 | [1.000, 1.000] | 1 |
| hit@1 | 0.250 | [0.000, 0.750] | 4 |
| hit@8 | 1.000 | [1.000, 1.000] | 4 |
| mrr | 0.625 | [0.500, 0.875] | 4 |
| ndcg@8 | 0.620 | [0.448, 0.731] | 4 |
| precision@8 | 0.156 | [0.125, 0.219] | 4 |
| recall@8 | 0.875 | [0.625, 1.000] | 4 |
| relevance | 1.000 | [1.000, 1.000] | 1 |
| unnecessary_abstention | 0.000 | [0.000, 0.000] | 2 |

### exact_term

| metric | mean | 95% CI | n |
| --- | ---: | ---: | ---: |
| abstained | 0.250 | [0.000, 0.750] | 4 |
| answered_without_citations | 0.000 | [0.000, 0.000] | 3 |
| citations_valid | 1.000 | [1.000, 1.000] | 3 |
| correctness | 0.750 | [0.250, 1.000] | 4 |
| faithfulness | 0.833 | [0.500, 1.000] | 3 |
| hit@1 | 0.000 | [0.000, 0.000] | 4 |
| hit@8 | 0.250 | [0.000, 0.750] | 4 |
| mrr | 0.036 | [0.000, 0.107] | 4 |
| ndcg@8 | 0.051 | [0.000, 0.153] | 4 |
| precision@8 | 0.031 | [0.000, 0.094] | 4 |
| recall@8 | 0.125 | [0.000, 0.375] | 4 |
| relevance | 1.000 | [1.000, 1.000] | 3 |
| unnecessary_abstention | 0.250 | [0.000, 0.750] | 4 |

### lookup

| metric | mean | 95% CI | n |
| --- | ---: | ---: | ---: |
| abstained | 0.000 | [0.000, 0.000] | 4 |
| answered_without_citations | 0.000 | [0.000, 0.000] | 4 |
| citations_valid | 1.000 | [1.000, 1.000] | 4 |
| correctness | 1.000 | [1.000, 1.000] | 4 |
| faithfulness | 1.000 | [1.000, 1.000] | 4 |
| hit@1 | 0.250 | [0.000, 0.750] | 4 |
| hit@8 | 0.750 | [0.250, 1.000] | 4 |
| mrr | 0.438 | [0.125, 0.750] | 4 |
| ndcg@8 | 0.515 | [0.158, 0.815] | 4 |
| precision@8 | 0.094 | [0.031, 0.125] | 4 |
| recall@8 | 0.750 | [0.250, 1.000] | 4 |
| relevance | 1.000 | [1.000, 1.000] | 4 |
| unnecessary_abstention | 0.000 | [0.000, 0.000] | 4 |

### multi_hop

| metric | mean | 95% CI | n |
| --- | ---: | ---: | ---: |
| abstained | 0.000 | [0.000, 0.000] | 1 |
| answered_without_citations | 0.000 | [0.000, 0.000] | 1 |
| citations_valid | 1.000 | [1.000, 1.000] | 1 |
| correctness | 1.000 | [1.000, 1.000] | 1 |
| faithfulness | 1.000 | [1.000, 1.000] | 1 |
| hit@1 | 0.250 | [0.000, 0.750] | 4 |
| hit@8 | 1.000 | [1.000, 1.000] | 4 |
| mrr | 0.500 | [0.333, 0.833] | 4 |
| ndcg@8 | 0.308 | [0.186, 0.519] | 4 |
| precision@8 | 0.156 | [0.125, 0.219] | 4 |
| recall@8 | 0.327 | [0.232, 0.458] | 4 |
| relevance | 1.000 | [1.000, 1.000] | 1 |
| unnecessary_abstention | 0.000 | [0.000, 0.000] | 1 |

### unanswerable

| metric | mean | 95% CI | n |
| --- | ---: | ---: | ---: |
| abstained | 1.000 | [1.000, 1.000] | 1 |
| correct_abstention | 1.000 | [1.000, 1.000] | 1 |
| missed_abstention | 0.000 | [0.000, 0.000] | 1 |

## Worst 10 failures

### pilot-010 (conceptual, answerable)

**Question:** Why does PEP 621 require dynamic metadata to be declared explicitly?

**Reference:** To distinguish metadata that will be supplied later from metadata that is simply missing.

**Error:** `LLMError`

**Retrieved sections:**

- ❌ [1] Storing project metadata in pyproject.toml > Specification > Details > ``dynamic`` (`74f7628b9d5e0341-0023`)
- ✅ [2] Storing project metadata in pyproject.toml > Motivation (`74f7628b9d5e0341-0002`)
- ❌ [3] Storing project metadata in pyproject.toml (`74f7628b9d5e0341-0000`)
- ❌ [4] Dependency Groups in pyproject.toml > Deferred Ideas > Why not support Dependency Group Includes in ``[project.dependencies]`` or ``[project.optional-dependencies]``? (`291eff3d2334240d-0034`)
- ❌ [5] Inline script metadata > Rejected Ideas > Why not use a requirements file for dependencies? (`4ef54cafa35d2932-0032`)
- ❌ [6] Version Identification and Dependency Specification > Version scheme > Version ordering across different metadata versions (`a5feae5ef825dc18-0035`)
- ❌ [7] Storing project metadata in pyproject.toml > Rejected Ideas > Require build back-ends to update ``pyproject.toml`` when generating an sdist (`74f7628b9d5e0341-0044`)
- ❌ [8] Storing project metadata in pyproject.toml > Rejected Ideas > Have the ``dynamic`` field only require specifying missing required fields (`74f7628b9d5e0341-0037`)

**Answer (answered, citations: 74f7628b9d5e0341-0002):** PEP 621 requires that any metadata not statically specified be listed in `dynamic` because this disambiguates the intent of unspecified metadata—when any metadata could be dynamic, you could never tell if an absent field was omitted on purpose or just not yet provided. By requiring dynamic metadata to be explicitly declared, the PEP removes this ambiguity. This also supports the PEP's broader motivation of encouraging users toward static metadata (for speed, ease of specification, unambiguity, and deterministic consumption by build back-ends), so raising the 'cost' of declaring something dynamic is seen as acceptable since users should be biased toward providing static metadata.

**Metrics:** abstained=0.00, answered_without_citations=0.00, citations_valid=1.00, hit@1=0.00, hit@8=1.00, mrr=0.50, ndcg@8=0.39, precision@8=0.12, recall@8=0.50, unnecessary_abstention=0.00

### pilot-011 (conceptual, answerable)

**Question:** According to PEP 380, why is a simple loop that re-yields values insufficient for full generator delegation?

**Reference:** It does not by itself handle the caller's send(), throw() and close() interactions with the subgenerator.

**Error:** `BudgetStoppedError`

**Retrieved sections:**

- ❌ [1] Syntax for Delegating to a Subgenerator > Abstract (`0f8f3036fc38a3de-0001`)
- ✅ [2] Syntax for Delegating to a Subgenerator > Motivation (`0f8f3036fc38a3de-0003`)
- ❌ [3] Syntax for Delegating to a Subgenerator > Proposal (`0f8f3036fc38a3de-0004`)
- ❌ [4] Syntax for Delegating to a Subgenerator > Rationale > Optimisations (`0f8f3036fc38a3de-0014`)
- ❌ [5] Syntax for Delegating to a Subgenerator > Alternative Proposals (`0f8f3036fc38a3de-0019`)
- ❌ [6] Syntax for Delegating to a Subgenerator > Rationale > Generators as Threads (`0f8f3036fc38a3de-0011`)
- ❌ [7] Asynchronous Generators > Specification > asyncio (`36159518962f7552-0010`)
- ❌ [8] The "with" Statement > Generator Decorator (`9b8996160cdfb03e-0016`)

**Metrics:** hit@1=0.00, hit@8=1.00, mrr=0.50, ndcg@8=0.63, precision@8=0.12, recall@8=1.00

### pilot-012 (conceptual, answerable)

**Question:** Why does PEP 723 propose metadata inside standalone scripts?

**Reference:** So tools can discover a script's runtime requirements without a separate project file or tool-specific metadata format.

**Error:** `BudgetStoppedError`

**Retrieved sections:**

- ❌ [1] Inline script metadata > Footnotes (`4ef54cafa35d2932-0037`)
- ✅ [2] Inline script metadata > Motivation (`4ef54cafa35d2932-0002`)
- ❌ [3] Inline script metadata > Abstract (`4ef54cafa35d2932-0001`)
- ❌ [4] Inline script metadata > Backwards Compatibility (`4ef54cafa35d2932-0010`)
- ❌ [5] Storing project metadata in pyproject.toml > Specification > Details > Entry points (`74f7628b9d5e0341-0019`)
- ❌ [6] Inline script metadata > Rejected Ideas > Why not use a comment block resembling requirements.txt? (`4ef54cafa35d2932-0018`)
- ❌ [7] Inline script metadata > Rejected Ideas > Why not just set up a Python project with a ``pyproject.toml``? (`4ef54cafa35d2932-0028`)
- ❌ [8] Inline script metadata > Rejected Ideas > Why not use a comment block resembling requirements.txt? (`4ef54cafa35d2932-0022`)

**Metrics:** hit@1=0.00, hit@8=1.00, mrr=0.50, ndcg@8=0.63, precision@8=0.12, recall@8=1.00

### pilot-013 (comparison, answerable)

**Question:** What type-annotation features do PEP 585 and PEP 604 add?

**Reference:** PEP 585 adds generic parameter syntax to standard collections; PEP 604 adds X | Y syntax for union types.

**Error:** `BudgetStoppedError`

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

### pilot-014 (comparison, answerable)

**Question:** What asynchronous features do PEP 525 and PEP 530 add?

**Reference:** PEP 525 adds asynchronous generators; PEP 530 adds asynchronous comprehensions and generator expressions.

**Error:** `BudgetStoppedError`

**Retrieved sections:**

- ✅ [1] Asynchronous Comprehensions > Abstract (`6b38213d6c03bb44-0001`)
- ❌ [2] Asynchronous Comprehensions > Acceptance (`6b38213d6c03bb44-0007`)
- ❌ [3] Asynchronous Generators > Acceptance (`36159518962f7552-0024`)
- ❌ [4] Asynchronous Comprehensions (`6b38213d6c03bb44-0000`)
- ❌ [5] Asynchronous Comprehensions > Specification > Asynchronous Comprehensions (`6b38213d6c03bb44-0003`)
- ❌ [6] Asynchronous Generators (`36159518962f7552-0000`)
- ❌ [7] Asynchronous Generators > Design Considerations > Why the ``asend()`` and ``athrow()`` methods are necessary (`36159518962f7552-0022`)
- ❌ [8] Coroutines with async and await syntax > Rationale and Goals (`b6d5d84d24a46b97-0003`)

**Metrics:** hit@1=1.00, hit@8=1.00, mrr=1.00, ndcg@8=0.61, precision@8=0.12, recall@8=0.50

### pilot-015 (comparison, answerable)

**Question:** Where do PEP 621 and PEP 723 place metadata?

**Reference:** PEP 621 places project core metadata in pyproject.toml; PEP 723 embeds script metadata in the script itself.

**Error:** `BudgetStoppedError`

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

### pilot-016 (comparison, answerable)

**Question:** Which is the pattern-matching specification and which is the tutorial: PEP 634 or PEP 636?

**Reference:** PEP 634 is the specification; PEP 636 is the tutorial.

**Error:** `BudgetStoppedError`

**Retrieved sections:**

- ✅ [1] Structural Pattern Matching: Tutorial > Abstract (`6851e97d3527eed9-0001`)
- ✅ [2] Structural Pattern Matching: Specification > Abstract (`efde821a3005f52a-0001`)
- ❌ [3] Structural Pattern Matching: Motivation and Rationale > Abstract (`0b9e8fe8ec7fded3-0001`)
- ❌ [4] Structural Pattern Matching: Tutorial > Tutorial > Matching builtin classes (`6851e97d3527eed9-0019`)
- ❌ [5] Structural Pattern Matching: Tutorial > Tutorial > Adding a UI: Matching objects (`6851e97d3527eed9-0014`)
- ❌ [6] Structural Pattern Matching: Motivation and Rationale > Rationale (`0b9e8fe8ec7fded3-0007`)
- ❌ [7] Structural Pattern Matching: Tutorial > Tutorial > Matching multiple patterns (`6851e97d3527eed9-0005`)
- ❌ [8] Structural Pattern Matching: Tutorial > Tutorial > Capturing matched sub-patterns (`6851e97d3527eed9-0011`)

**Metrics:** hit@1=1.00, hit@8=1.00, mrr=1.00, ndcg@8=1.00, precision@8=0.25, recall@8=1.00

### pilot-018 (multi_hop, answerable)

**Question:** Which native-coroutine PEP does PEP 525 build on, and does that earlier proposal require a specific event-loop implementation?

**Reference:** PEP 492. It is not tied to a specific event-loop implementation.

**Error:** `BudgetStoppedError`

**Retrieved sections:**

- ✅ [1] Coroutines with async and await syntax > Abstract (`b6d5d84d24a46b97-0001`)
- ❌ [2] Asynchronous Generators > Specification > asyncio (`36159518962f7552-0010`)
- ❌ [3] Coroutines with async and await syntax > Specification > Coroutine objects > Differences from generators (`b6d5d84d24a46b97-0022`)
- ❌ [4] Coroutines with async and await syntax > Specification (`b6d5d84d24a46b97-0004`)
- ❌ [5] Coroutines with async and await syntax > Specification > New Standard Library Functions (`b6d5d84d24a46b97-0026`)
- ❌ [6] Coroutines with async and await syntax > Design Considerations > Coroutine-generators (`b6d5d84d24a46b97-0040`)
- ❌ [7] Asynchronous Generators > Specification > Finalization (`36159518962f7552-0008`)
- ❌ [8] Coroutines with async and await syntax > Rationale and Goals (`b6d5d84d24a46b97-0003`)

**Metrics:** hit@1=1.00, hit@8=1.00, mrr=1.00, ndcg@8=0.61, precision@8=0.12, recall@8=0.50

### pilot-019 (multi_hop, answerable)

**Question:** Which rationale PEP does PEP 636 point to, and what type-or-shape checking idiom does its Motivation section show match replacing?

**Reference:** PEP 635. It shows match replacing an if/elif/else chain that checks an object's type or shape.

**Error:** `BudgetStoppedError`

**Retrieved sections:**

- ❌ [1] Structural Pattern Matching: Specification > Abstract (`efde821a3005f52a-0001`)
- ❌ [2] Structural Pattern Matching: Motivation and Rationale > Abstract (`0b9e8fe8ec7fded3-0001`)
- ✅ [3] Structural Pattern Matching: Motivation and Rationale > Motivation (`0b9e8fe8ec7fded3-0002`)
- ❌ [4] Structural Pattern Matching: Motivation and Rationale > Rationale > Patterns > OR Patterns (`0b9e8fe8ec7fded3-0024`)
- ❌ [5] Structural Pattern Matching: Motivation and Rationale > Rationale > The Match Statement > Match Semantics (`0b9e8fe8ec7fded3-0015`)
- ❌ [6] Variadic Generics > Alternatives (`9117768b87185ae7-0040`)
- ❌ [7] Structural Pattern Matching: Motivation and Rationale > Rationale > Patterns (`0b9e8fe8ec7fded3-0018`)
- ✅ [8] Structural Pattern Matching: Tutorial > Abstract (`6851e97d3527eed9-0001`)

**Metrics:** hit@1=0.00, hit@8=1.00, mrr=0.33, ndcg@8=0.25, precision@8=0.25, recall@8=0.33

### pilot-020 (multi_hop, answerable)

**Question:** Which type-hinting PEP does PEP 544 extend, and does that earlier proposal require runtime type checking?

**Reference:** PEP 484. It does not require runtime type checking.

**Error:** `BudgetStoppedError`

**Retrieved sections:**

- ❌ [1] Syntax for Variable Annotations > Rationale > Non-goals (`4e9bac3fbbd66adf-0005`)
- ❌ [2] Postponed Evaluation of Annotations > Rationale and Goals > Non-typing usage of annotations (`24cedd106580f3ea-0005`)
- ✅ [3] Type Hints > Abstract (`a25e032f504686c8-0001`)
- ❌ [4] Protocols: Structural subtyping (static duck typing) > Runtime Implementation of Protocol Classes > Introspection (`a35c304214b4044a-0035`)
- ❌ [5] Type Hinting Generics In Standard Collections > Rejected alternatives > Making ``isinstance(obj, list[str])`` perform a runtime type check (`e26e4b478a435481-0016`)
- ❌ [6] Type Hints > Compatibility with other uses of function annotations (`a25e032f504686c8-0046`)
- ❌ [7] Arbitrary Literal String Type > Rejected Alternatives > Runtime Checkable ``LiteralString`` (`037f79d0f8ba9656-0026`)
- ❌ [8] Protocols: Structural subtyping (static duck typing) > Existing Approaches to Structural Subtyping (`a35c304214b4044a-0008`)

**Metrics:** hit@1=0.00, hit@8=1.00, mrr=0.33, ndcg@8=0.23, precision@8=0.12, recall@8=0.33
