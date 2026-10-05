# Chunking and contextual-header ablation

Real local BM25 retrieval, no model API calls. The same 24 owner-approved questions are used throughout; 20 answerable items contribute metrics. Original labels are unchanged. This is an exploratory pilot, not a held-out benchmark.

| Variant | Hit@1 | Hit@8 | MRR | MRR change vs 400 | Paired 95% CI |
| --- | --- | --- | --- | --- | --- |
| bm25_tokens400 | 25% | 70% | 0.420 | baseline | - |
| bm25_tokens250 | 40% | 60% | 0.458 | +0.039 | [-0.049, +0.142] |
| bm25_tokens600 | 25% | 65% | 0.406 | -0.014 | [-0.033, +0.000] |
| bm25_noheader | 30% | 65% | 0.446 | +0.026 | [-0.014, +0.087] |

The default uses a 400 approximate-token budget, 15% overlap and title/section headers in index text. The 250/600 variants change only the token budget; noheader changes only the indexing header. Structure boundaries can produce smaller chunks. Dedup settings, BM25 parameters and top-eight cutoff are fixed. Dataset manifests preserve source hashes and chunking parameters.

Paired intervals use 1,000 resamples and seed 0. Questions overlap in topic; the sample is small, labels are not exhaustive, and no multiplicity correction is applied. Recall and nDCG denominators change with chunking, so the headline comparison uses Hit@k and MRR. Answer quality and abstention are not measured.

Retrieval mode and reranking ablations are documented in [baseline results](baseline-results.md). These experiments do not justify changing defaults without a broader reviewed evaluation set.

## Saved runs

- `20261005T030406Z_bm25_only`
- `20261005T072446Z_bm25_tokens250`
- `20261005T072458Z_bm25_tokens600`
- `20261005T072507Z_bm25_noheader`
