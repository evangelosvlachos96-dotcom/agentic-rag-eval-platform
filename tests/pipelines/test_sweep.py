"""Real tiny BM25 sweep verifies provenance and overwrite protection offline."""

from pathlib import Path

import pytest

from ragplatform.evals.models import EvalItem, SourceRef
from ragplatform.evals.results import read_results
from ragplatform.ingestion.chunking import ChunkingConfig
from ragplatform.ingestion.loaders import load_file
from ragplatform.pipelines.sweep import ChunkingVariant, run_variant


def test_retrieval_variant_saves_run_and_refuses_overwrite(tmp_path: Path) -> None:
    raw = tmp_path / "raw"
    raw.mkdir()
    source = raw / "topic.txt"
    source.write_text(
        "Python supports context managers with enter and exit methods.", encoding="utf-8"
    )
    (raw / "other.txt").write_text("Volcanoes produce lava.", encoding="utf-8")
    (raw / "third.txt").write_text("Oceans contain salt water.", encoding="utf-8")
    doc = load_file(source)
    item = EvalItem(
        id="fixture",
        question="What supports context managers?",
        reference_answer="Python",
        category="lookup",
        created_by="human",
        relevant_sources=[SourceRef(doc_id=doc.document.id)],
    )
    variant = ChunkingVariant(name="test_bm25", chunking=ChunkingConfig(max_tokens=250))
    run_dir = tmp_path / "run"
    result = run_variant(
        variant,
        raw_dir=raw,
        processed_root=tmp_path / "processed",
        run_dir=run_dir,
        items=[item],
        eval_version="test",
        repo_dir=tmp_path,
    )
    assert result.llm_calls == 0
    assert result.retrieval_only
    assert result.generator_model is None
    assert result.metrics["hit@1"].mean == 1
    assert read_results(run_dir)[0].answer is None
    assert (run_dir / "dataset-manifest.json").exists()
    with pytest.raises(FileExistsError, match="already exists"):
        run_variant(
            variant,
            raw_dir=raw,
            processed_root=tmp_path / "processed",
            run_dir=run_dir,
            items=[item],
            eval_version="test",
            repo_dir=tmp_path,
        )
