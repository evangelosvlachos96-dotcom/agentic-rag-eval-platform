"""Evals: measuring retrieval and generation quality separately.

Planned responsibilities (Milestone 5 and 6):

- retrieval metrics: recall@k, MRR, nDCG
- generation checks: programmatic faithfulness and citation validity first,
  then an LLM judge with bias mitigation (position swaps, rubric scoring)
- reliability metrics for agents: pass@k and pass^k
- bootstrap confidence intervals so differences between runs are not noise
"""
