# eval_sets/

Versioned evaluation sets, tracked in git. Each set is a folder named by a
semantic version, containing the items and a manifest with a content hash so
results are always attributable to an exact set.

Planned layout (Milestone 5):

```
eval_sets/
  <name>/
    v1/
      manifest.json    # name, version, sha256 of items, creation date, notes
      items.jsonl      # {id, query, relevant_chunk_ids, reference_answer, ...}
    v2/
      ...
```

Rules:

- never edit a published version in place; create a new one
- every item carries a stable `id` so labels can be joined across versions
- keep sets small enough to review by hand; quality over quantity
