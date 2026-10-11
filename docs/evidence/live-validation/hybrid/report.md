# Eval run `20261010T154612Z_live_hybrid`

- config: `live_hybrid`
- created: 2026-10-10T15:57:34+00:00
- git: `c1193279bda76c5d2ca549e84668607de824a111` (dirty)
- dataset version: `27b46e65f45d`
- eval set: `v1` @ `1f48f2e04ef7` (24 items)
- prompts: {'answer': 'answer_v1', 'judge_faithfulness': 'judge_faithfulness_v1', 'judge_correctness': 'judge_correctness_v1', 'judge_relevance': 'judge_relevance_v1'}
- generator: `claude-sonnet-5`  judge: `claude-haiku-4-5`  provider: `cached(budgeted(anthropic))`
- retrieval only: False
- LLM calls: 84 (cache hits 0, misses 84); tokens in/out: 151509/20010; estimated cost: 0.36544299999999996
- errors: 0; items whose labels matched no chunk: 0
- bootstrap: 1000 resamples, seed 0

## Usage accounting

Token totals include cached responses; incremental cost excludes cache hits. Rates are applied separately per requested model. Hidden SDK retries and provider billing adjustments are not independently observable.

Calls with unknown usage: 0

| Model | Total input | Total output | Billable input | Billable output |
| --- | ---: | ---: | ---: | ---: |
| claude-haiku-4-5 | 65655 | 14404 | 65655 | 14404 |
| claude-sonnet-5 | 85854 | 5606 | 85854 | 5606 |

## Metrics

| metric | mean | 95% CI | n |
| --- | ---: | ---: | ---: |
| abstained | 0.208 | [0.042, 0.375] | 24 |
| answered_without_citations | 0.000 | [0.000, 0.000] | 19 |
| citations_valid | 1.000 | [1.000, 1.000] | 19 |
| correct_abstention | 1.000 | [1.000, 1.000] | 4 |
| correctness | 0.950 | [0.850, 1.000] | 20 |
| faithfulness | 0.934 | [0.873, 0.987] | 19 |
| hit@1 | 0.400 | [0.200, 0.600] | 20 |
| hit@8 | 0.800 | [0.600, 0.950] | 20 |
| missed_abstention | 0.000 | [0.000, 0.000] | 4 |
| mrr | 0.562 | [0.392, 0.733] | 20 |
| ndcg@8 | 0.515 | [0.357, 0.665] | 20 |
| precision@8 | 0.138 | [0.100, 0.175] | 20 |
| recall@8 | 0.639 | [0.450, 0.804] | 20 |
| relevance | 1.000 | [1.000, 1.000] | 19 |
| unnecessary_abstention | 0.050 | [0.000, 0.150] | 20 |

## By category

### comparison

| metric | mean | 95% CI | n |
| --- | ---: | ---: | ---: |
| abstained | 0.000 | [0.000, 0.000] | 4 |
| answered_without_citations | 0.000 | [0.000, 0.000] | 4 |
| citations_valid | 1.000 | [1.000, 1.000] | 4 |
| correctness | 1.000 | [1.000, 1.000] | 4 |
| faithfulness | 0.812 | [0.625, 1.000] | 4 |
| hit@1 | 0.250 | [0.000, 0.750] | 4 |
| hit@8 | 0.500 | [0.000, 1.000] | 4 |
| mrr | 0.333 | [0.000, 0.750] | 4 |
| ndcg@8 | 0.378 | [0.000, 0.755] | 4 |
| precision@8 | 0.125 | [0.000, 0.250] | 4 |
| recall@8 | 0.500 | [0.000, 1.000] | 4 |
| relevance | 1.000 | [1.000, 1.000] | 4 |
| unnecessary_abstention | 0.000 | [0.000, 0.000] | 4 |

### conceptual

| metric | mean | 95% CI | n |
| --- | ---: | ---: | ---: |
| abstained | 0.000 | [0.000, 0.000] | 4 |
| answered_without_citations | 0.000 | [0.000, 0.000] | 4 |
| citations_valid | 1.000 | [1.000, 1.000] | 4 |
| correctness | 1.000 | [1.000, 1.000] | 4 |
| faithfulness | 0.875 | [0.750, 1.000] | 4 |
| hit@1 | 0.500 | [0.000, 1.000] | 4 |
| hit@8 | 1.000 | [1.000, 1.000] | 4 |
| mrr | 0.750 | [0.500, 1.000] | 4 |
| ndcg@8 | 0.724 | [0.509, 0.939] | 4 |
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
| hit@1 | 0.250 | [0.000, 0.750] | 4 |
| hit@8 | 0.750 | [0.250, 1.000] | 4 |
| mrr | 0.438 | [0.125, 0.812] | 4 |
| ndcg@8 | 0.454 | [0.108, 0.847] | 4 |
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
| hit@8 | 0.750 | [0.250, 1.000] | 4 |
| mrr | 0.458 | [0.125, 0.750] | 4 |
| ndcg@8 | 0.533 | [0.158, 0.815] | 4 |
| precision@8 | 0.094 | [0.031, 0.125] | 4 |
| recall@8 | 0.750 | [0.250, 1.000] | 4 |
| relevance | 1.000 | [1.000, 1.000] | 4 |
| unnecessary_abstention | 0.000 | [0.000, 0.000] | 4 |

### multi_hop

| metric | mean | 95% CI | n |
| --- | ---: | ---: | ---: |
| abstained | 0.000 | [0.000, 0.000] | 4 |
| answered_without_citations | 0.000 | [0.000, 0.000] | 4 |
| citations_valid | 1.000 | [1.000, 1.000] | 4 |
| correctness | 1.000 | [1.000, 1.000] | 4 |
| faithfulness | 1.000 | [1.000, 1.000] | 4 |
| hit@1 | 0.750 | [0.250, 1.000] | 4 |
| hit@8 | 1.000 | [1.000, 1.000] | 4 |
| mrr | 0.833 | [0.500, 1.000] | 4 |
| ndcg@8 | 0.485 | [0.337, 0.632] | 4 |
| precision@8 | 0.219 | [0.156, 0.250] | 4 |
| recall@8 | 0.446 | [0.310, 0.583] | 4 |
| relevance | 1.000 | [1.000, 1.000] | 4 |
| unnecessary_abstention | 0.000 | [0.000, 0.000] | 4 |

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

- ❌ [1] Syntax for Variable Annotations > Rejected/Postponed Proposals (`4e9bac3fbbd66adf-0020`)
- ❌ [2] Deferred Evaluation Of Annotations Using Descriptors > Overview > Comparison Of Annotation Semantics (`ad23617867325d80-0005`)
- ❌ [3] Deferred Evaluation Of Annotations Using Descriptors > Overview > Comparison Of Annotation Semantics (`ad23617867325d80-0006`)
- ❌ [4] Allow writing union types as ``X | Y`` > Motivation (`1b96f779896ff109-0002`)
- ❌ [5] Deferred Evaluation Of Annotations Using Descriptors > Overview > Comparison Of Annotation Semantics (`ad23617867325d80-0007`)
- ❌ [6] Syntax for Variable Annotations > Specification (`4e9bac3fbbd66adf-0006`)
- ❌ [7] Implementing PEP 649 > Behavior of dataclass field types (`80014392886f031e-0039`)
- ❌ [8] Flexible function and variable annotations > Motivation (`18ed3b62aa90c0eb-0002`)

**Answer (ABSTAINED, citations: none):** The context does not cover this.

**Metrics:** abstained=1.00, correctness=0.00, hit@1=0.00, hit@8=0.00, mrr=0.00, ndcg@8=0.00, precision@8=0.00, recall@8=0.00, unnecessary_abstention=1.00

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

**Answer (answered, citations: 1b96f779896ff109-0002):** PEP 585 adds exposure of parameters to generics at runtime. PEP 604 adds the ability to write union types using the `X | Y` syntax instead of the more verbose `Union[X, Y]`.

**Correctness judge (correct):** The candidate's characterization of PEP 585 as 'exposure of parameters to generics at runtime' is more technically precise but describes a mechanism rather than the feature itself. The reference's description of 'generic parameter syntax to standard collections' better captures what PEP 585 enables users to do - namely, use standard collections (like list, dict) directly with type parameters (e.g., list[int]) instead of importing from typing module. However, the candidate's description is not contradictory; runtime parameter access is indeed part of what PEP 585 provides. For PEP 604, both answers correctly identify the `X | Y` syntax feature, with the candidate providing helpful additional context about the alternative syntax. Both essential facts from the reference are present in the candidate, even if expressed differently.

**Unsupported claims:**

- PEP 604 adds the ability to write union types using the `X | Y` syntax instead of the more verbose `Union[X, Y]`. — The context mentions the `X | Y` syntax in the title 'Allow writing union types as ``X | Y``' and discusses that users must use `Union[X, Y]` under current syntax, but it does not explicitly state that PEP 604 adds this feature. The context chunk is titled as if it were about PEP 604, but does not actually name PEP 604 or attribute the `X | Y` syntax feature to it.

**Metrics:** abstained=0.00, answered_without_citations=0.00, citations_valid=1.00, correctness=1.00, faithfulness=0.50, hit@1=0.00, hit@8=0.00, mrr=0.00, ndcg@8=0.00, precision@8=0.00, recall@8=0.00, relevance=1.00, unnecessary_abstention=0.00

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

**Answer (answered, citations: 74f7628b9d5e0341-0000, 74f7628b9d5e0341-0003, 4ef54cafa35d2932-0000, 4ef54cafa35d2932-0024, 4ef54cafa35d2932-0022):** PEP 621 places metadata in the project's `pyproject.toml` file (standardizing core metadata fields there), while PEP 723 places metadata inline within the script file itself, rather than in pyproject.toml or a comment block resembling requirements.txt — it explicitly rejected reusing the pyproject.toml metadata standard, noting that doing so would be a misuse of that metadata and would require fields like name and version that don't fit single scripts.

**Correctness judge (correct):** The candidate answer contains all essential facts from the reference: (1) PEP 621 places metadata in pyproject.toml, and (2) PEP 723 embeds/places metadata in the script itself. The candidate does not contradict the reference on any core point. The additional detail about PEP 723 rejecting reuse of pyproject.toml metadata standard and the reasoning behind it is extra information beyond what the reference provides, but this does not contradict or undermine the reference answer and represents correct supplementary context.

**Unsupported claims:**

- PEP 723 rejected reusing pyproject.toml metadata because fields like name and version don't fit single scripts — While the context states that name and version fields are required in the metadata standard and changing that would require its own PEP, it does not explicitly explain that these fields don't fit single scripts—this is an inference the answer makes but not directly stated in the context.

**Metrics:** abstained=0.00, answered_without_citations=0.00, citations_valid=1.00, correctness=1.00, faithfulness=0.75, hit@1=0.00, hit@8=0.00, mrr=0.00, ndcg@8=0.00, precision@8=0.00, recall@8=0.00, relevance=1.00, unnecessary_abstention=0.00

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

**Answer (answered, citations: 9b8996160cdfb03e-0019):** The context management protocol consists of the `__enter__()` and `__exit__()` methods; objects implementing these are called "context managers."

**Correctness judge (correct):** The candidate correctly identifies both essential methods that form the context-manager protocol described by PEP 343: __enter__() and __exit__(). The candidate provides the same core factual content as the reference, simply with additional context about what objects implementing these methods are called. The candidate does not contradict any point in the reference and fully answers the question asked.

**Metrics:** abstained=0.00, answered_without_citations=0.00, citations_valid=1.00, correctness=1.00, faithfulness=1.00, hit@1=0.00, hit@8=0.00, mrr=0.00, ndcg@8=0.00, precision@8=0.00, recall@8=0.00, relevance=1.00, unnecessary_abstention=0.00

### pilot-009 (conceptual, answerable)

**Question:** Why does PEP 526 favor annotation syntax over type comments for parsing?

**Reference:** Its rationale says annotation syntax can be parsed with ast, while type comments require a custom parser.

**Retrieved sections:**

- ✅ [1] Syntax for Variable Annotations > Rationale (`4e9bac3fbbd66adf-0004`)
- ❌ [2] Syntax for Variable Annotations > Abstract (`4e9bac3fbbd66adf-0003`)
- ❌ [3] Syntax for Variable Annotations > Rejected/Postponed Proposals (`4e9bac3fbbd66adf-0019`)
- ✅ [4] Syntax for Variable Annotations > Rationale > Non-goals (`4e9bac3fbbd66adf-0005`)
- ❌ [5] Inline script metadata > Rejected Ideas > Why not use a comment block resembling requirements.txt? (`4ef54cafa35d2932-0021`)
- ❌ [6] Type Hints > Type comments (`a25e032f504686c8-0047`)
- ❌ [7] Syntax for Variable Annotations > Notice for Reviewers (`4e9bac3fbbd66adf-0002`)
- ❌ [8] Type Hints > Abstract (`a25e032f504686c8-0001`)

**Answer (answered, citations: 4e9bac3fbbd66adf-0004):** Because type comments aren't actually part of the language, so a tool wanting to parse them needs a custom parser instead of simply being able to use Python's built-in `ast` module, as would be possible with dedicated annotation syntax.

**Correctness judge (correct):** The candidate answer captures the essential facts from the reference: (1) annotation syntax can be parsed with the `ast` module, and (2) type comments require a custom parser. The candidate provides additional context about why this difference exists (type comments aren't part of the language), but this elaboration doesn't contradict the reference—it explains the underlying reason. The candidate directly addresses why PEP 526 favors annotation syntax over type comments, which matches the reference answer's core point.

**Unsupported claims:**

- Dedicated annotation syntax would allow using the built-in `ast` module — While the context implies this by contrasting the custom parser requirement for type comments with the benefits of making annotation syntax 'a core part of the language,' it does not explicitly state that the built-in `ast` module can be used with dedicated annotation syntax.

**Metrics:** abstained=0.00, answered_without_citations=0.00, citations_valid=1.00, correctness=1.00, faithfulness=0.67, hit@1=1.00, hit@8=1.00, mrr=1.00, ndcg@8=0.88, precision@8=0.25, recall@8=1.00, relevance=1.00, unnecessary_abstention=0.00

### pilot-010 (conceptual, answerable)

**Question:** Why does PEP 621 require dynamic metadata to be declared explicitly?

**Reference:** To distinguish metadata that will be supplied later from metadata that is simply missing.

**Retrieved sections:**

- ❌ [1] Storing project metadata in pyproject.toml > Specification > Details > ``dynamic`` (`74f7628b9d5e0341-0023`)
- ✅ [2] Storing project metadata in pyproject.toml > Motivation (`74f7628b9d5e0341-0002`)
- ❌ [3] Storing project metadata in pyproject.toml > Specification > Details > ``dynamic`` (`74f7628b9d5e0341-0022`)
- ❌ [4] Version Identification and Dependency Specification > Version scheme > Version ordering across different metadata versions (`a5feae5ef825dc18-0035`)
- ❌ [5] Inline script metadata > Rejected Ideas > Why not reuse core metadata fields? (`4ef54cafa35d2932-0024`)
- ❌ [6] Storing project metadata in pyproject.toml > Rejected Ideas > Have the ``dynamic`` field only require specifying missing required fields (`74f7628b9d5e0341-0037`)
- ❌ [7] Storing project metadata in pyproject.toml > Specification (`74f7628b9d5e0341-0005`)
- ❌ [8] Storing project metadata in pyproject.toml (`74f7628b9d5e0341-0000`)

**Answer (answered, citations: 74f7628b9d5e0341-0002, 74f7628b9d5e0341-0022, 74f7628b9d5e0341-0023):** PEP 621 requires that any field left unspecified be explicitly listed in `dynamic` so that tools can distinguish intentional omission from an oversight. Since the PEP's design goal is to push users toward specifying metadata statically (for speed, ease of specification, unambiguity, and deterministic consumption), raising the cost of declaring something dynamic is acceptable, as it "disambiguates the intent when metadata goes unspecified" — otherwise one could never know if an absent field was meant to be dynamic or simply forgotten. Correspondingly, if a field isn't listed in `dynamic`, a build back-end cannot fill it in on the user's behalf; `dynamic` is the only mechanism allowing a tool to supply metadata, and the user must explicitly opt into that.

**Correctness judge (correct):** The candidate answer contains the essential fact from the reference: that the requirement exists to distinguish between metadata that will be supplied later (dynamic) versus metadata that is simply missing (omission/oversight). The candidate expands on this with additional accurate details about PEP 621's design philosophy and implementation, but all of this is supplementary and consistent with the reference answer. The core reasoning—distinguishing intentional dynamic metadata from forgotten/missing metadata—is present and clearly articulated in both answers.

**Unsupported claims:**

- PEP 621 requires that any field left unspecified be explicitly listed in `dynamic` — The context states that requiring the distinction helps with disambiguation, but does not explicitly state that ALL unspecified fields must be listed in dynamic. The context says dynamic metadata must be specified, not that all unspecified fields must be listed there. This is slightly overstated.

**Metrics:** abstained=0.00, answered_without_citations=0.00, citations_valid=1.00, correctness=1.00, faithfulness=0.83, hit@1=0.00, hit@8=1.00, mrr=0.50, ndcg@8=0.39, precision@8=0.12, recall@8=0.50, relevance=1.00, unnecessary_abstention=0.00
