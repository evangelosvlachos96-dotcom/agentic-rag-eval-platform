"""Tests for ragplatform.config."""

from __future__ import annotations

from pathlib import Path

import pytest
from pydantic import ValidationError

from ragplatform.config import Settings, get_settings


def test_defaults_require_no_api_key(settings: Settings) -> None:
    assert settings.anthropic_api_key is None
    assert settings.has_anthropic_key is False
    assert settings.anthropic_model == "claude-opus-5"
    assert settings.anthropic_judge_model == "claude-sonnet-5"
    assert settings.embedding_model.startswith("sentence-transformers/")
    assert settings.log_level == "INFO"
    assert settings.data_dir == Path("data")


def test_environment_overrides_defaults(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    monkeypatch.setenv("ANTHROPIC_MODEL", "claude-sonnet-5")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    monkeypatch.setenv("DATA_DIR", str(tmp_path / "rag-data"))

    settings = Settings(_env_file=None)

    assert settings.has_anthropic_key is True
    assert settings.anthropic_api_key is not None
    assert settings.anthropic_api_key.get_secret_value() == "test-key"
    assert settings.anthropic_model == "claude-sonnet-5"
    assert settings.log_level == "DEBUG"
    assert settings.data_dir == tmp_path / "rag-data"


def test_secret_is_masked_in_repr(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ANTHROPIC_API_KEY", "super-secret")
    settings = Settings(_env_file=None)
    assert "super-secret" not in repr(settings)
    assert "super-secret" not in str(settings)


def test_empty_api_key_counts_as_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ANTHROPIC_API_KEY", "")
    assert Settings(_env_file=None).has_anthropic_key is False


def test_invalid_log_level_is_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LOG_LEVEL", "LOUD")
    with pytest.raises(ValidationError):
        Settings(_env_file=None)


def test_settings_are_immutable(settings: Settings) -> None:
    with pytest.raises(ValidationError):
        settings.log_level = "DEBUG"  # type: ignore[misc]


def test_get_settings_is_cached() -> None:
    get_settings.cache_clear()
    try:
        assert get_settings() is get_settings()
    finally:
        get_settings.cache_clear()
