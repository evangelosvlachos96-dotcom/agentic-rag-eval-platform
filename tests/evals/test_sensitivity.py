"""Safeguards and hand-checkable scores for offline label diagnostics."""

from pathlib import Path

import pytest

from ragplatform.evals.results import read_results
from ragplatform.evals.sensitivity import ProposedSource, rescore_saved

EVIDENCE = Path(__file__).resolve().parents[2] / "docs/evidence/pilot-baselines/bm25_only"


def test_saved_rescore_is_exact_and_immutable() -> None:
    results = read_results(EVIDENCE)
    before = [r.model_dump_json() for r in results]
    proposal = ProposedSource(
        item_id="pilot-003",
        doc_id="96c61294f2cd86dd",
        section_path="Specification",
        evidence="Reviewed source text",
        rationale="Defines both qualifiers",
    )
    scores = rescore_saved(results, [proposal])
    item = next(s for s in scores if s.item_id == "pilot-003")
    assert item.original["hit@8"] == 0
    assert item.proposed["hit@8"] == 1
    assert item.proposed["mrr"] == 0.5
    assert len(scores) == 20
    assert before == [r.model_dump_json() for r in results]
    wrong = proposal.model_copy(update={"section_path": "Specification > Missing"})
    assert all(s.original == s.proposed for s in rescore_saved(results, [wrong]))
    with pytest.raises(ValueError, match="Duplicate proposed"):
        rescore_saved(results, [proposal, proposal])
    with pytest.raises(ValueError, match="known answerable"):
        rescore_saved(results, [proposal.model_copy(update={"item_id": "pilot-024"})])
    with pytest.raises(ValueError, match="Duplicate result"):
        rescore_saved(results + results, [])
    with pytest.raises(ValueError, match="positive"):
        rescore_saved(results, [], k=0)


def test_unchanged_labels_reproduce_saved_metrics() -> None:
    results = read_results(EVIDENCE)
    scores = {s.item_id: s for s in rescore_saved(results, [])}
    for result in results:
        if result.answerable:
            assert scores[result.item_id].original == scores[result.item_id].proposed
            for metric, value in scores[result.item_id].original.items():
                assert value == result.metrics[metric]
