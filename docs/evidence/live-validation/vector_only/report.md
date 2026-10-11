# Eval run `20261010T153558Z_live_vector_only`

- config: `live_vector_only`
- created: 2026-10-10T15:46:09+00:00
- git: `c1193279bda76c5d2ca549e84668607de824a111` (dirty)
- dataset version: `27b46e65f45d`
- eval set: `v1` @ `1f48f2e04ef7` (24 items)
- prompts: {'answer': 'answer_v1', 'judge_faithfulness': 'judge_faithfulness_v1', 'judge_correctness': 'judge_correctness_v1', 'judge_relevance': 'judge_relevance_v1'}
- generator: `claude-sonnet-5`  judge: `claude-haiku-4-5`  provider: `cached(budgeted(anthropic))`
- retrieval only: False
- LLM calls: 76 (cache hits 0, misses 76); tokens in/out: 123497/17037; estimated cost: 0.301249
- errors: 0; items whose labels matched no chunk: 0
- bootstrap: 1000 resamples, seed 0

## Usage accounting

Token totals include cached responses; incremental cost excludes cache hits. Rates are applied separately per requested model. Hidden SDK retries and provider billing adjustments are not independently observable.

Calls with unknown usage: 0

| Model | Total input | Total output | Billable input | Billable output |
| --- | ---: | ---: | ---: | ---: |
| claude-haiku-4-5 | 52810 | 12661 | 52810 | 12661 |
| claude-sonnet-5 | 70687 | 4376 | 70687 | 4376 |

## Metrics

| metric | mean | 95% CI | n |
| --- | ---: | ---: | ---: |
| abstained | 0.292 | [0.125, 0.500] | 24 |
| answered_without_citations | 0.000 | [0.000, 0.000] | 17 |
| citations_valid | 1.000 | [1.000, 1.000] | 17 |
| correct_abstention | 1.000 | [1.000, 1.000] | 4 |
| correctness | 0.850 | [0.700, 1.000] | 20 |
| faithfulness | 1.000 | [1.000, 1.000] | 17 |
| hit@1 | 0.250 | [0.050, 0.450] | 20 |
| hit@8 | 0.750 | [0.550, 0.950] | 20 |
| missed_abstention | 0.000 | [0.000, 0.000] | 4 |
| mrr | 0.430 | [0.264, 0.589] | 20 |
| ndcg@8 | 0.443 | [0.281, 0.604] | 20 |
| precision@8 | 0.131 | [0.094, 0.169] | 20 |
| recall@8 | 0.606 | [0.414, 0.792] | 20 |
| relevance | 1.000 | [1.000, 1.000] | 17 |
| unnecessary_abstention | 0.150 | [0.000, 0.300] | 20 |

## By category

### comparison

| metric | mean | 95% CI | n |
| --- | ---: | ---: | ---: |
| abstained | 0.250 | [0.000, 0.750] | 4 |
| answered_without_citations | 0.000 | [0.000, 0.000] | 3 |
| citations_valid | 1.000 | [1.000, 1.000] | 3 |
| correctness | 0.750 | [0.250, 1.000] | 4 |
| faithfulness | 1.000 | [1.000, 1.000] | 3 |
| hit@1 | 0.250 | [0.000, 0.750] | 4 |
| hit@8 | 0.500 | [0.000, 1.000] | 4 |
| mrr | 0.312 | [0.000, 0.750] | 4 |
| ndcg@8 | 0.367 | [0.000, 0.750] | 4 |
| precision@8 | 0.125 | [0.000, 0.250] | 4 |
| recall@8 | 0.500 | [0.000, 1.000] | 4 |
| relevance | 1.000 | [1.000, 1.000] | 3 |
| unnecessary_abstention | 0.250 | [0.000, 0.750] | 4 |

### conceptual

| metric | mean | 95% CI | n |
| --- | ---: | ---: | ---: |
| abstained | 0.000 | [0.000, 0.000] | 4 |
| answered_without_citations | 0.000 | [0.000, 0.000] | 4 |
| citations_valid | 1.000 | [1.000, 1.000] | 4 |
| correctness | 1.000 | [1.000, 1.000] | 4 |
| faithfulness | 1.000 | [1.000, 1.000] | 4 |
| hit@1 | 0.000 | [0.000, 0.000] | 4 |
| hit@8 | 1.000 | [1.000, 1.000] | 4 |
| mrr | 0.411 | [0.232, 0.500] | 4 |
| ndcg@8 | 0.489 | [0.360, 0.618] | 4 |
| precision@8 | 0.156 | [0.125, 0.219] | 4 |
| recall@8 | 0.875 | [0.625, 1.000] | 4 |
| relevance | 1.000 | [1.000, 1.000] | 4 |
| unnecessary_abstention | 0.000 | [0.000, 0.000] | 4 |

### exact_term

| metric | mean | 95% CI | n |
| --- | ---: | ---: | ---: |
| abstained | 0.250 | [0.000, 0.750] | 4 |
| answered_without_citations | 0.000 | [0.000, 0.000] | 3 |
| citations_valid | 1.000 | [1.000, 1.000] | 3 |
| correctness | 0.750 | [0.250, 1.000] | 4 |
| faithfulness | 1.000 | [1.000, 1.000] | 3 |
| hit@1 | 0.500 | [0.000, 1.000] | 4 |
| hit@8 | 0.750 | [0.250, 1.000] | 4 |
| mrr | 0.550 | [0.100, 1.000] | 4 |
| ndcg@8 | 0.559 | [0.119, 1.000] | 4 |
| precision@8 | 0.094 | [0.031, 0.125] | 4 |
| recall@8 | 0.625 | [0.250, 1.000] | 4 |
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
| hit@8 | 0.500 | [0.000, 1.000] | 4 |
| mrr | 0.312 | [0.000, 0.750] | 4 |
| ndcg@8 | 0.358 | [0.000, 0.750] | 4 |
| precision@8 | 0.062 | [0.000, 0.125] | 4 |
| recall@8 | 0.500 | [0.000, 1.000] | 4 |
| relevance | 1.000 | [1.000, 1.000] | 4 |
| unnecessary_abstention | 0.000 | [0.000, 0.000] | 4 |

### multi_hop

| metric | mean | 95% CI | n |
| --- | ---: | ---: | ---: |
| abstained | 0.250 | [0.000, 0.750] | 4 |
| answered_without_citations | 0.000 | [0.000, 0.000] | 3 |
| citations_valid | 1.000 | [1.000, 1.000] | 3 |
| correctness | 0.750 | [0.250, 1.000] | 4 |
| faithfulness | 1.000 | [1.000, 1.000] | 3 |
| hit@1 | 0.250 | [0.000, 0.750] | 4 |
| hit@8 | 1.000 | [1.000, 1.000] | 4 |
| mrr | 0.562 | [0.375, 0.875] | 4 |
| ndcg@8 | 0.441 | [0.208, 0.694] | 4 |
| precision@8 | 0.219 | [0.156, 0.250] | 4 |
| recall@8 | 0.530 | [0.226, 0.833] | 4 |
| relevance | 1.000 | [1.000, 1.000] | 3 |
| unnecessary_abstention | 0.250 | [0.000, 0.750] | 4 |

### unanswerable

| metric | mean | 95% CI | n |
| --- | ---: | ---: | ---: |
| abstained | 1.000 | [1.000, 1.000] | 4 |
| correct_abstention | 1.000 | [1.000, 1.000] | 4 |
| missed_abstention | 0.000 | [0.000, 0.000] | 4 |

## Worst 6 failures

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

**Answer (ABSTAINED, citations: none):** The context does not cover this.

**Metrics:** abstained=1.00, correctness=0.00, hit@1=0.00, hit@8=0.00, mrr=0.00, ndcg@8=0.00, precision@8=0.00, recall@8=0.00, unnecessary_abstention=1.00

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

**Answer (ABSTAINED, citations: none):** The provided context does not cover PEP 585 or PEP 604.

**Metrics:** abstained=1.00, correctness=0.00, hit@1=0.00, hit@8=0.00, mrr=0.00, ndcg@8=0.00, precision@8=0.00, recall@8=0.00, unnecessary_abstention=1.00

### pilot-019 (multi_hop, answerable)

**Question:** Which rationale PEP does PEP 636 point to, and what type-or-shape checking idiom does its Motivation section show match replacing?

**Reference:** PEP 635. It shows match replacing an if/elif/else chain that checks an object's type or shape.

**Retrieved sections:**

- ❌ [1] Structural Pattern Matching: Motivation and Rationale > Abstract (`0b9e8fe8ec7fded3-0001`)
- ✅ [2] Structural Pattern Matching: Tutorial > Abstract (`6851e97d3527eed9-0001`)
- ❌ [3] Structural Pattern Matching: Specification > Abstract (`efde821a3005f52a-0001`)
- ❌ [4] Structural Pattern Matching: Motivation and Rationale > Rationale > The Match Statement (`0b9e8fe8ec7fded3-0012`)
- ❌ [5] Structural Pattern Matching: Motivation and Rationale (`0b9e8fe8ec7fded3-0000`)
- ❌ [6] Structural Pattern Matching: Motivation and Rationale > Rationale > The Match Statement (`0b9e8fe8ec7fded3-0009`)
- ❌ [7] Structural Pattern Matching: Motivation and Rationale > History and Context (`0b9e8fe8ec7fded3-0049`)
- ❌ [8] Structural Pattern Matching: Motivation and Rationale > Rationale > The Match Statement (`0b9e8fe8ec7fded3-0010`)

**Answer (ABSTAINED, citations: none):** The tutorial (PEP 636) points to PEP 635 as the companion "motivation and rationale" document. However, the retrieved context does not include the specific portion of PEP 635's Motivation section describing a type-or-shape checking idiom that match is shown to replace, so I cannot answer that part.

**Metrics:** abstained=1.00, correctness=0.00, hit@1=0.00, hit@8=1.00, mrr=0.50, ndcg@8=0.19, precision@8=0.12, recall@8=0.17, unnecessary_abstention=1.00

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

**Answer (answered, citations: 9b8996160cdfb03e-0022):** The context-manager protocol uses the `__enter__` and `__exit__` methods; objects implementing them are called "context managers," and a decorator (`contextlib.contextmanager`) can turn a generator function into a context manager factory.

**Correctness judge (correct):** The candidate correctly identifies both essential methods (__enter__ and __exit__) that form the context-manager protocol as described in PEP 343. The candidate provides additional correct information about context managers and the contextlib.contextmanager decorator, which does not contradict the reference and does not constitute hedging. The core answer directly addresses the question asked.

**Metrics:** abstained=0.00, answered_without_citations=0.00, citations_valid=1.00, correctness=1.00, faithfulness=1.00, hit@1=0.00, hit@8=0.00, mrr=0.00, ndcg@8=0.00, precision@8=0.00, recall@8=0.00, relevance=1.00, unnecessary_abstention=0.00

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

**Answer (answered, citations: 74f7628b9d5e0341-0000, 74f7628b9d5e0341-0003):** PEP 621 specifies storing project core metadata in the `pyproject.toml` file.

**Correctness judge (correct):** The candidate answer correctly identifies that PEP 621 uses `pyproject.toml` for project core metadata, which matches the essential fact in the reference answer. The candidate provides the same core information with additional context about what the file is used for, but does not contradict or hedge the reference answer. The answer directly and definitively states which file is used.

**Metrics:** abstained=0.00, answered_without_citations=0.00, citations_valid=1.00, correctness=1.00, faithfulness=1.00, hit@1=0.00, hit@8=0.00, mrr=0.00, ndcg@8=0.00, precision@8=0.00, recall@8=0.00, relevance=1.00, unnecessary_abstention=0.00

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

**Answer (answered, citations: 74f7628b9d5e0341-0000, 4ef54cafa35d2932-0000):** PEP 621 ("Storing project metadata in pyproject.toml") places project metadata in the `pyproject.toml` file, while PEP 723 ("Inline script metadata") places metadata directly inline within a script file itself, rather than in a separate project file.

**Correctness judge (correct):** The candidate answer contains all essential facts from the reference: (1) PEP 621 places metadata in pyproject.toml, and (2) PEP 723 embeds metadata in the script itself. The candidate provides additional helpful context by including the PEP titles and clarifying the contrast between the two approaches (separate project file vs. inline), but this extra detail does not contradict the reference. The core information is accurate and complete.

**Metrics:** abstained=0.00, answered_without_citations=0.00, citations_valid=1.00, correctness=1.00, faithfulness=1.00, hit@1=0.00, hit@8=0.00, mrr=0.00, ndcg@8=0.00, precision@8=0.00, recall@8=0.00, relevance=1.00, unnecessary_abstention=0.00
