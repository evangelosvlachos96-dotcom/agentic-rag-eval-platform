"""Prove that dry runs, declined spending and retrieval baselines never create an LLM."""

from pathlib import Path

import pytest
from typer.testing import CliRunner

from ragplatform.cli import app, eval_cmds
from ragplatform.config import Settings
from ragplatform.ingestion.pipeline import ingest_directory
from ragplatform.retrieval.index import build_index

REPO = Path(__file__).resolve().parents[2]


@pytest.fixture
def offline_cli(monkeypatch: pytest.MonkeyPatch, tmp_path: Path, fixture_corpus_dir: Path) -> Path:
    settings = Settings(
        _env_file=None,
        data_dir=tmp_path / "data",
        eval_sets_dir=REPO / "eval_sets",
        configs_dir=REPO / "configs",
        experiments_dir=tmp_path / "experiments",
    )
    directory = ingest_directory(fixture_corpus_dir, settings.processed_dir).output_dir
    build_index(directory)
    monkeypatch.setattr(eval_cmds, "get_settings", lambda: settings)
    monkeypatch.setattr(eval_cmds, "resolve_dataset_dir", lambda _: directory)

    def forbidden(*args: object, **kwargs: object) -> None:
        raise AssertionError("An offline or unapproved command constructed an LLM provider")

    monkeypatch.setattr(eval_cmds, "_provider", forbidden)
    return settings.experiments_dir


def test_candidate_dry_run_and_declined_confirmation(offline_cli: Path) -> None:
    runner = CliRunner()
    args = [
        "eval",
        "generate-candidates",
        "--n",
        "2",
        "--taxonomy",
        str(REPO / "eval_sets" / "taxonomy_v1.yaml"),
    ]
    dry = runner.invoke(app, [*args, "--dry-run"])
    assert dry.exit_code == 0, dry.output
    assert "zero LLM calls" in dry.output
    assert "Planning allowance" in dry.output
    declined = runner.invoke(app, args, input="n\n")
    assert declined.exit_code == 1
    assert "Aborted" in declined.output
    assert not offline_cli.exists()


def test_baseline_is_retrieval_only(offline_cli: Path) -> None:
    result = CliRunner().invoke(app, ["eval", "baseline", "--eval-set", "fixture"])
    assert result.exit_code == 0, result.output
    assert "zero Anthropic calls" in result.output
    summaries = list(offline_cli.glob("runs/*/summary.json"))
    assert len(summaries) == 1
    from ragplatform.evals.results import RunSummary

    summary = RunSummary.model_validate_json(summaries[0].read_text(encoding="utf-8"))
    assert summary.llm_calls == 0
    assert summary.retrieval_only


def test_generation_dry_run_and_decline_never_construct_provider(offline_cli: Path) -> None:
    args = [
        "eval",
        "run",
        "--eval-set",
        "fixture",
        "--config",
        str(REPO / "configs/bm25_only.yaml"),
    ]
    runner = CliRunner()
    dry = runner.invoke(app, [*args, "--dry-run"])
    assert dry.exit_code == 0, dry.output
    assert "zero LLM calls" in dry.output
    assert "not a spending cap" in dry.output
    declined = runner.invoke(app, args, input="n\n")
    assert declined.exit_code == 1
    assert "Aborted" in declined.output
    assert not offline_cli.exists()
