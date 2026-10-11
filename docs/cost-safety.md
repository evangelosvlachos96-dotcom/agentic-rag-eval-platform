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
The original development phase used no paid requests. The owner subsequently
authorized the [bounded live validation](live-validation.md) on 2026-10-10.

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

## Bounded live session

The live-validation script adds persistent pre-call reservations, a shared USD 3
limit, no SDK retries, and five seconds between completed paid requests. Unknown
usage stops automatic progress. After confirming the old process has stopped, an
operator can explicitly resume while keeping the full failed-call reservation.
This never refunds an unknown request, resets the budget, or clears an overrun.
Both the interrupted run and the recovery note remain in published evidence.
Reported usage cost and retained unknown-cost allowances are shown separately.
