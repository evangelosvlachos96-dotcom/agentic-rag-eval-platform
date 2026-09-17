# experiments/

Outputs of `rag eval run` live here. Everything in this directory except this
README is gitignored.

```
experiments/
  runs/
    <timestamp>_<config>/     # e.g. 20260917T085855Z_bm25_only
      config.json             # RunConfig snapshot (retrieval, generation, judge)
      results.jsonl           # one ItemResult per eval item: retrieved sections with
                              # relevance flags, answer, checks, judge verdicts, metrics
      summary.json            # provenance (git commit + dirty flag, dataset version,
                              # eval set version, prompt versions, models, provider),
                              # metrics with bootstrap CIs, per-category breakdown,
                              # LLM calls, cache hits/misses, tokens, estimated cost
      report.md               # the same plus the 10 worst failures
```

`rag eval compare <run_a> <run_b>` prints per-metric deltas with paired
bootstrap intervals. Runs made with `--mock-llm` are placeholders and say so in
their report. Reports worth keeping should be copied into `docs/` and committed.
