# Cost accounting and offline planning

`rag eval run --dry-run` performs local retrieval and prints a planning allowance
without constructing an LLM provider. Declining the generation confirmation also
avoids provider construction. Example:

```powershell
rag eval run --config configs/bm25_only.yaml --eval-set v1 --dataset-version 27b46e65f45d --dry-run
```

The allowance is **not a spending cap**. It uses approximate input token counts and
fixed typical output allowances. Structured-output repairs, longer answers and
provider SDK retries can increase usage. Verify model availability and current
rates before authorizing a paid run; the CLI prints the pricing snapshot date.
No paid evaluation was executed during this development work.

Run accounting observes each completion before output parsing. Consequently:

- malformed responses and repair attempts retain their reported token usage;
- generator and judge tokens are priced at their respective configured rates;
- cached responses count toward logical usage, but not estimated new spend;
- provider failures with no usage produce an unknown cost, not zero;
- a judge failure preserves an already-generated answer and its programmatic checks.

The summary includes total and billable usage by requested model and calls with
unknown usage. Provider call counts do not expose hidden SDK retry attempts. Costs
are estimates from configured rates, not invoice reconciliation; prompt caching,
provider-specific billing adjustments and failed requests may require account-side
verification.

Cache filenames now include a provider namespace. A fake completion cannot satisfy
a real-provider request with the same content. Older unnamespaced cache files are
not reused because they lack that isolation. This can cause a future real run to
make fresh calls; review its plan first. Cached fake agent trajectories remain
explicitly marked as placeholders.
