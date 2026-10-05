# Label sensitivity diagnostic

Exploratory assistant-proposed annotation, not an approved evaluation. One confirmed gap only; the remaining pooled passages are unreviewed. Original labels and baseline files are unchanged. No API calls or new retrieval.

| Configuration | Original Hit@8 | Proposed Hit@8 | Original MRR | Proposed MRR |
| --- | --- | --- | --- | --- |
| bm25_only | 70% | 75% | 0.420 | 0.445 |
| vector_only | 75% | 75% | 0.430 | 0.430 |
| hybrid | 80% | 80% | 0.562 | 0.575 |
| hybrid_rerank | 70% | 70% | 0.502 | 0.502 |

The review packet contains 425 unique question/passage pairs pooled from the four saved top-eight rankings. It hides system names and ranks. Pooling can still miss relevant passages outside those rankings.

Only pilot-003 / PEP 655 / Specification is added in this diagnostic, with exact section matching. Evidence and per-item changes are in diagnostic.json. An annotation change is not an improvement in the retrieval system.

Recall, nDCG and complete-source coverage are not recomputed: additional alternatives do not define exhaustive relevance or independent required facts.

Next: review pooled evidence and keep proposed annotations separate until accepted. Next, test the M6 agent with a fake provider before paid evaluation.
