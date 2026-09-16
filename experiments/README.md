# experiments/

Outputs of experiment runs live here: metrics, per-item results, trajectories
and reports. Everything in this directory except this README is gitignored.

Planned layout (Milestone 8 and 9):

```
experiments/
  <run-id>/            # e.g. 2026-09-16T10-30_hybrid-rerank
    config.json        # full resolved configuration + git revision
    metrics.json       # aggregate metrics with confidence intervals
    results.jsonl      # one line per eval item
    report.md          # human-readable summary
```

Reports worth keeping should be copied into `docs/` and committed.
