# Active review draft: pilot_v2.jsonl

Use **pilot_v2.jsonl** for the final human review. `pilot_v1.jsonl` is retained only as
the superseded draft; do not review or combine both files. Their item IDs intentionally match.

The v2 pass narrows questions and reference answers to source-supported claims, replaces
the four multi-hop questions with explicit reference chains, and removes relative dates.
The owner has accepted all 24 v2 candidates. Decisions are recorded in
`pilot_v2.jsonl.review.json`, and frozen labels are in `eval_sets/v1`.
Candidate files remain unchanged as provenance. No Anthropic API calls were made for either draft.

- [Concise question-and-answer list](../../docs/pilot-questions.md)
- [Full source evidence](../../docs/pilot-review.md)

```bash
uv run rag eval review eval_sets/candidates/pilot_v2.jsonl --eval-set v1
```

Four entries test abstention for information absent from the PEP corpus. Their attached
passages are background, not evidence for a factual answer. Multi-hop questions use two
documents but remain a pilot: human review must assess ambiguity and actual difficulty.
