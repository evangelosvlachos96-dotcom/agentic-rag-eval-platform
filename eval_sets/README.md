# eval_sets/

Versioned evaluation sets, tracked in git.

```
eval_sets/
  taxonomy_v1.yaml         # question categories: definition, decision rule, example
  candidates/
    <timestamp>.jsonl      # synthetic candidates written by `rag eval generate-candidates`
    <timestamp>.jsonl.review.json   # review decisions, so `rag eval review` can resume
  fixture/
    items.jsonl            # 5 hand-written items over tests/fixtures/corpus (pipeline tests only)
    manifest.json
  v1/                      # created by `rag eval review`; does not exist yet
    items.jsonl            # one EvalItem per line
    manifest.json          # name, version (sha256[:12] of items.jsonl), counts, updated_at
```

Item schema (`ragplatform.evals.models.EvalItem`): `id`, `question`,
`reference_answer`, `relevant_sources` (list of `{doc_id, section_path}`),
`category`, `difficulty`, `answerable`, `created_by` (`human` |
`synthetic_reviewed`), `notes`.

Rules:

- relevance is labeled by `doc_id` + `section_path`, never by chunk id, so
  labels survive re-chunking (a chunk matches when its section equals or is
  nested under the labeled one)
- candidates are not eval items; only `rag eval review` writes to
  `<name>/items.jsonl`
- never edit a published set in place; create `v2`
- every item carries a stable `id` (the candidate id) so labels can be joined
  across versions
- keep sets small enough to review by hand; target 60 to 100 items with at
  least 10% unanswerable
