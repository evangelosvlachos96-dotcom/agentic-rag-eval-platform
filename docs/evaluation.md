# Evaluation methodology

This document explains how the harness in `ragplatform.evals` measures the
system and why it is built the way it is. No numbers appear here on purpose:
the real eval set (`eval_sets/v1`) has not been generated or reviewed yet, and
every figure in `experiments/runs/` so far comes from the fixture corpus with a
placeholder LLM.

## 1. Retrieval and generation are scored separately

A wrong answer has two possible causes: the right passage was never retrieved,
or it was retrieved and misused. The harness keeps those apart:

- **Retrieval metrics** (recall@k, precision@k, hit@k, MRR, nDCG@k) score the
  ranked chunk list against relevance labels and never involve the LLM.
- **Generation checks and judges** score the answer given the chunks it saw.

`rag eval run --retrieval-only` runs the first half alone, with no API key.

## 2. Relevance is labeled by source, not by chunk id

An eval item lists `relevant_sources`, each a `doc_id` plus a `section_path`
such as `"Specification > Syntax"`. A retrieved chunk counts as relevant when
its document matches and its section path equals, or is nested under, a
labeled path (an empty path means "anywhere in the document").

Chunk ids are a function of the chunker's parameters; the moment the token
budget or overlap changes, every id changes and chunk-level labels are worthless.
Document ids are content hashes and section paths come from the headings, so
source-level labels survive re-chunking. This is what makes the chunking
ablation (M9) possible: the same eval set scores every chunk size.

For metrics that need a denominator (recall, ideal DCG) the harness expands the
labels against the current dataset version: `n_relevant` is the number of
chunks in the corpus that fall under the labeled sources. Items whose labels
match no chunk at all are counted in `n_unmatched_labels` and score zero, so
label drift is visible instead of silently inflating results.

Unanswerable items are retrieved (so their chunks appear in the report) but
excluded from retrieval metrics: there is no correct chunk to find.

## 3. Programmatic checks come before LLM judges

Whatever code can verify, code verifies, because code is free, deterministic
and never biased by wording:

| Check | Meaning |
| --- | --- |
| `citations_valid` | every cited id named a chunk that was actually provided (invalid ones are removed by the generator and recorded) |
| `answered_without_citations` | the system answered but cited nothing |
| `correct_abstention` | unanswerable item and the system abstained |
| `missed_abstention` | unanswerable item but the system answered |
| `unnecessary_abstention` | answerable item but the system abstained |

Only after these run do the judges get involved, and only when the system
actually answered. An abstention on an answerable item is scored as
`correctness = 0` without a judge call; there is nothing to grade. When
retrieval returns no chunks the generator abstains without calling the LLM.

## 4. Judge design and bias mitigations

Three judges, each a versioned prompt in `ragplatform/prompts/` recorded in
every run:

- **Faithfulness** (`judge_faithfulness_v1`): the answer is split into atomic
  claims; for each the judge must quote evidence from the retrieved context and
  explain before marking it supported or not. Score = supported / total claims.
  An answer with no checkable claims gets no score rather than a free 1.0.
- **Correctness** (`judge_correctness_v1`): binary, graded against the human
  reference answer with an explicit three-part rubric (essential facts present,
  no contradiction, no non-answer). Only runs for answerable items.
- **Answer relevance** (`judge_relevance_v1`): binary, does the answer address
  the question asked.

Mitigations for known judge biases:

- **Evidence and reasoning before the verdict.** The JSON field order forces the
  model to quote and argue first; the boolean comes last.
- **Rubric, not opinion.** Correctness is measured against a reference the
  human reviewer wrote, not against the judge's own knowledge.
- **No length reward.** Every prompt says so explicitly, and faithfulness is a
  ratio, so adding claims cannot raise it.
- **Separate judge model.** `JudgeConfig.model` (or `ANTHROPIC_JUDGE_MODEL`) is
  configured independently of the generator, so the generator is not grading
  itself.
- **Validated output with one repair retry.** Malformed JSON is sent back once
  with the validation error; a second failure is recorded as an item error, not
  silently scored.
- **Deterministic repeats.** Every call is cached on disk by the hash of the full
  request, so re-running a config re-uses the same judgements. Current Claude
  models and the SDK no longer accept a temperature parameter, so the cache and
  fixed prompts are what make repeats reproducible, not a temperature of zero.

What is *not* done yet: position swapping only matters for pairwise judges,
and none of the three judges compares two candidates. Judge-human agreement
(Cohen's kappa) is Milestone 7; until it is measured, judge scores are signals,
not ground truth.

## 5. Bootstrap confidence intervals

Every aggregate metric is reported with a 95% percentile bootstrap interval:
the per-item values are resampled with replacement 1000 times (seeded, so the
interval is reproducible), the mean of each resample is taken, and the 2.5th and
97.5th percentiles bound the interval.

`rag eval compare` uses a **paired** bootstrap: it resamples item indices and
recomputes `mean(B) - mean(A)` on the same items each time. Item difficulty
that both runs share cancels out, which is much tighter than comparing two
independent intervals. A delta is called distinguishable from noise only when
its interval excludes zero. With the eval set sizes this project targets
(60 to 100 items), small deltas will usually not be distinguishable, and the
report says so instead of rounding them up to an improvement.

## 6. Building the eval set

1. `rag eval generate-candidates` samples chunks round-robin across documents
   (so long PEPs do not dominate) and cycles target categories through the
   taxonomy in `eval_sets/taxonomy_v1.yaml`, with a fixed share of
   unanswerable prompts. The LLM writes a question, a reference answer and a
   category for each. Output goes to `eval_sets/candidates/<timestamp>.jsonl`
   with the source chunk attached.
2. `rag eval review` shows each candidate with its source text. The reviewer
   accepts, edits (question, answer, category, sources) or rejects, and can
   quit and resume. Accepted items are appended to `eval_sets/v1/items.jsonl`
   with `created_by = synthetic_reviewed`.

Candidates are not eval items. Nothing is evaluated against a candidate file,
and no synthetic question enters the set without a human decision.

## 7. Current limitations

- **No real eval set yet.** `eval_sets/v1` does not exist; `eval_sets/fixture`
  is five hand-written items over the three-document test corpus and exists
  only to exercise the pipeline.
- **Candidates come from single chunks.** Multi-hop and comparison questions
  need the reviewer to add the second source by hand.
- **Chunk-level recall can undercount.** A long labeled section spans several
  chunks; retrieving one good chunk of five scores recall 0.2 even if that
  chunk answers the question. `hit@k` and MRR are the better "did we find it"
  signals; recall is kept because it is the textbook definition.
- **Judges are uncalibrated.** Agreement with human labels has not been
  measured (M7).
- **Cost estimates are approximate.** They use the ~4-characters-per-token
  heuristic on the real prompts and assume every item is answered.
- **Sequential LLM calls.** The runner awaits one call at a time; the async
  batch runner with retries is Milestone 8.
- **`--mock-llm` numbers mean nothing.** The fake provider returns canned JSON
  so the pipeline can be exercised without a key. Reports from such runs carry
  a placeholder warning and must never be quoted.
