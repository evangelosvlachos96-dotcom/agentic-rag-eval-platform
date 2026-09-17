"""Tests for ragplatform.pipelines.run_config and the shipped configs/*.yaml."""

from __future__ import annotations

from pathlib import Path

import pytest
from pydantic import ValidationError

from ragplatform.pipelines.run_config import RunConfig, load_run_config

CONFIGS_DIR = Path(__file__).resolve().parents[2] / "configs"


@pytest.mark.parametrize(
    ("name", "mode", "rerank"),
    [
        ("bm25_only", "bm25", False),
        ("vector_only", "vector", False),
        ("hybrid", "hybrid", False),
        ("hybrid_rerank", "hybrid", True),
    ],
)
def test_shipped_configs_load(name: str, mode: str, rerank: bool) -> None:
    config = load_run_config(CONFIGS_DIR / f"{name}.yaml")
    assert config.name == name
    assert config.retrieval.mode == mode
    assert config.retrieval.rerank is rerank
    assert config.retrieval.candidate_k == 50
    assert config.retrieval.final_k == 8
    assert config.generation.prompt_version == "answer_v1"
    assert config.judge.model is None


def test_name_defaults_to_file_stem(tmp_path: Path) -> None:
    path = tmp_path / "my_run.yaml"
    path.write_text("retrieval:\n  mode: bm25\n", encoding="utf-8")
    config = load_run_config(path)
    assert config.name == "my_run"
    assert config.retrieval.mode == "bm25"


def test_unknown_keys_and_bad_values_are_rejected(tmp_path: Path) -> None:
    path = tmp_path / "bad.yaml"
    path.write_text("retrieval:\n  mode: bm25\n  typo_k: 3\n", encoding="utf-8")
    with pytest.raises(ValidationError):
        load_run_config(path)
    with pytest.raises(ValidationError):
        RunConfig.model_validate({"name": "x", "retrieval": {"mode": "graph"}})


def test_non_mapping_yaml_is_rejected(tmp_path: Path) -> None:
    path = tmp_path / "list.yaml"
    path.write_text("- a\n- b\n", encoding="utf-8")
    with pytest.raises(ValueError, match="mapping"):
        load_run_config(path)
