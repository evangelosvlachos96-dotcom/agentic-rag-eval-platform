"""Offline annotation operations. No model provider is constructed."""

from pathlib import Path

import typer

from ragplatform.data_quality.annotations import (
    AnnotationBatch,
    compare_annotations,
    export_batch,
    import_batch,
    save_batch,
)
from ragplatform.evals.results import read_summary
from ragplatform.ingestion.dataset import read_chunks, read_manifest

quality_app = typer.Typer(help="Offline annotation export, validation and agreement.")


@quality_app.command("export")
def export(run_dir: Path, dataset_dir: Path, output: Path) -> None:
    """Export blank judgments with actual source text for review."""
    if read_summary(run_dir).dataset_version != read_manifest(dataset_dir).dataset_version:
        raise typer.BadParameter("dataset does not match the run")
    batch = export_batch(run_dir, read_chunks(dataset_dir))
    save_batch(output, batch)
    typer.echo(f"Exported {len(batch.rows)} unreviewed items to {output}")


@quality_app.command("import")
def import_annotations(original: Path, reviewed: Path, output: Path) -> None:
    """Validate an edited batch and save separately; never alters approved evals."""
    blank = AnnotationBatch.model_validate_json(original.read_text(encoding="utf-8"))
    labels = AnnotationBatch.model_validate_json(reviewed.read_text(encoding="utf-8"))
    save_batch(output, import_batch(blank, labels))
    typer.echo(f"Validated {sum(r.verdict is not None for r in labels.rows)} judgments")


@quality_app.command("agreement")
def compare(left: Path, right: Path) -> None:
    """Report agreement for shared labeled IDs, with missingness counts."""
    a = AnnotationBatch.model_validate_json(left.read_text(encoding="utf-8"))
    b = AnnotationBatch.model_validate_json(right.read_text(encoding="utf-8"))
    typer.echo(compare_annotations(a, b).model_dump_json(indent=2))


@quality_app.command("judge-agreement")
def compare_judge(original: Path, reviewed: Path, run_dir: Path) -> None:
    """Compare accepted human judgments with saved judge outputs; no new judge calls."""
    import hashlib

    from ragplatform.data_quality.annotations import judge_agreement
    from ragplatform.evals.results import read_results

    blank = AnnotationBatch.model_validate_json(original.read_text(encoding="utf-8"))
    labels = AnnotationBatch.model_validate_json(reviewed.read_text(encoding="utf-8"))
    import_batch(blank, labels)
    digest = hashlib.sha256((run_dir / "results.jsonl").read_bytes()).hexdigest()
    if labels.results_sha256 != digest or labels.run_id != read_summary(run_dir).run_id:
        raise typer.BadParameter("reviewed batch does not match this run")
    typer.echo(judge_agreement(labels, read_results(run_dir)).model_dump_json(indent=2))
