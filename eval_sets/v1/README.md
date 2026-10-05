# Reviewed pilot v1

This set contains the 24 questions from candidate revision `pilot_v2.jsonl`.
The project owner accepted that revision in this chat with: "i accept them,
lets move with the nxt step". The acceptance was recorded through `rag eval review`.

- 24 accepted, 0 rejected, 0 pending; four items per category.
- 20 answerable questions contribute to retrieval metrics.
- Four unanswerable questions are retained for later generation/abstention evaluation.
- Dataset: `27b46e65f45d`; eval-set version: `1f48f2e04ef7`.
- All source labels passed the offline audit.
- Candidate and review-state records are retained under `eval_sets/candidates/`.

These are assistant-authored, owner-approved pilot labels. They have not received an
independent second annotation or judge-human calibration. The set is small, includes
overlapping topics and straightforward out-of-domain negatives, and does not support
broad production-quality claims. Source labels are not exhaustive: other passages may
also support an answer. Retrieval misses mean no **labeled** passage was retrieved,
not necessarily that all retrieved content was irrelevant.

Do not change these labels in response to baseline scores. Any further label review
should produce a new version and preserve the original runs.
