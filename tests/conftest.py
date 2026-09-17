"""Shared pytest fixtures."""

from __future__ import annotations

from pathlib import Path

import pytest

from ragplatform.config import Settings

FIXTURES_DIR = Path(__file__).parent / "fixtures"
FIXTURE_CORPUS_DIR = FIXTURES_DIR / "corpus"

# Every variable Settings reads. Cleared before each test so a developer's real
# environment (or .env) can never leak into unit tests.
_SETTINGS_ENV_VARS = (
    "ANTHROPIC_API_KEY",
    "ANTHROPIC_MODEL",
    "ANTHROPIC_JUDGE_MODEL",
    "EMBEDDING_MODEL",
    "RERANKER_MODEL",
    "DATA_DIR",
    "EVAL_SETS_DIR",
    "EXPERIMENTS_DIR",
    "CONFIGS_DIR",
    "LOG_LEVEL",
)


@pytest.fixture(autouse=True)
def _clean_settings_env(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in _SETTINGS_ENV_VARS:
        monkeypatch.delenv(name, raising=False)


@pytest.fixture
def settings() -> Settings:
    """Settings built from defaults only (no .env file, no environment)."""
    return Settings(_env_file=None)


@pytest.fixture
def fixture_corpus_dir() -> Path:
    return FIXTURE_CORPUS_DIR
