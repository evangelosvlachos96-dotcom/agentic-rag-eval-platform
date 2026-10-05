# Data quality workflow

The quality commands operate entirely on saved results. They do not construct a
model provider or modify approved evaluation items.

```powershell
rag quality export docs/evidence/pilot-baselines/hybrid data/processed/27b46e65f45d experiments/annotations.json
rag quality import experiments/annotations.json experiments/reviewed.json experiments/validated.json
rag quality agreement experiments/reviewer-a.json experiments/reviewer-b.json
rag quality judge-agreement experiments/annotations.json experiments/validated.json experiments/runs/RUN_ID
```

Exports contain questions, reference answers, generated answers when available,
and the actual retrieved passage text. Verdicts start null. Reviewers fill their
identity and kind (`human`, `assistant`, or `judge`) plus correctness verdicts and
notes. Import rejects changed evidence, altered provenance, unknown or duplicate
items, and correctness labels for a run with no generated answers. Imported
annotations remain separate from the original evaluation set.

The saved blank batch under `docs/evidence/data-quality` comes from the real hybrid
retrieval baseline. It contains **no generated answers and no human judgments**.
It is an evidence-review artifact; correctness cannot be annotated until there is
an answer to assess. Missing source labels are tracked separately in the label
sensitivity diagnostic.

Agreement uses shared labeled IDs and reports missing labels on each side. Cohen's
kappa is null for no paired labels or degenerate expected agreement of one; it is
never replaced with a misleading perfect score. Judge-human comparison uses saved
binary correctness judgments and excludes uncertain human labels. No real
judge-human agreement is reported because the required reviews and paid judge
outputs do not exist yet.

Failure signals distinguish unmatched source labels from labeled retrieval misses,
citation errors, abstention errors, execution errors and negative judge verdicts.
A labeled miss does not prove that the retrieved passages are irrelevant. Judge
signals are not human truth. Duplicate detection is conservative Unicode, case and
whitespace normalization, not a claim of semantic deduplication.
