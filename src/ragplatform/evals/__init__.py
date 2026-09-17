"""Evals: measuring retrieval and generation quality separately (Milestone 5).

- ``models``: :class:`EvalItem` with source-level relevance labels
- ``eval_set``: ``eval_sets/<name>/items.jsonl`` I/O and content-hash versions
- ``taxonomy``: the versioned question taxonomy (``eval_sets/taxonomy_v1.yaml``)
- ``relevance``: matching retrieved chunks to labeled sources (nested sections)
- ``metrics``: recall@k, precision@k, hit@k, MRR, nDCG@k as pure functions
- ``checks``: programmatic citation and abstention checks (no LLM)
- ``judges``: faithfulness, correctness and relevance LLM judges
- ``bootstrap``: seeded bootstrap CIs and paired bootstrap comparisons
- ``candidates`` / ``review``: synthetic candidate generation and human review
- ``estimate`` / ``runner`` / ``results`` / ``report`` / ``compare``: the run pipeline

Planned (Milestone 6): pass@k and pass^k for agent trajectories.
"""

from ragplatform.evals.bootstrap import bootstrap_ci, paired_bootstrap
from ragplatform.evals.metrics import hit_at_k, mrr, ndcg_at_k, precision_at_k, recall_at_k
from ragplatform.evals.models import EvalItem, SourceRef
from ragplatform.evals.runner import EvalRunner

__all__ = [
    "EvalItem",
    "EvalRunner",
    "SourceRef",
    "bootstrap_ci",
    "hit_at_k",
    "mrr",
    "ndcg_at_k",
    "paired_bootstrap",
    "precision_at_k",
    "recall_at_k",
]
