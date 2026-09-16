"""Application settings.

Settings are loaded with ``pydantic-settings`` from environment variables and,
if present, a ``.env`` file in the working directory. Environment variables
always take precedence over the file. Secrets are wrapped in ``SecretStr`` so
they never appear in logs or reprs.

Every module that needs configuration should call :func:`get_settings` rather
than reading ``os.environ`` directly; this keeps configuration testable.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


class Settings(BaseSettings):
    """Runtime configuration for the platform.

    Field names map 1:1 to upper-cased environment variables, e.g.
    ``anthropic_api_key`` is read from ``ANTHROPIC_API_KEY``.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        frozen=True,
    )

    # --- LLM provider -------------------------------------------------------
    anthropic_api_key: SecretStr | None = Field(
        default=None,
        description="Anthropic API key. Optional so that offline tooling works without it.",
    )
    anthropic_model: str = Field(
        default="claude-opus-5",
        description="Model used for answer generation and the agent loop.",
    )
    anthropic_judge_model: str = Field(
        default="claude-sonnet-5",
        description="Model used for LLM-as-judge evaluation.",
    )

    # --- Embeddings ---------------------------------------------------------
    embedding_model: str = Field(
        default="sentence-transformers/all-MiniLM-L6-v2",
        description="Local sentence-transformers model; no API key required.",
    )

    # --- Paths --------------------------------------------------------------
    data_dir: Path = Field(default=Path("data"), description="Root for raw/processed data.")
    eval_sets_dir: Path = Field(default=Path("eval_sets"), description="Versioned test sets.")
    experiments_dir: Path = Field(default=Path("experiments"), description="Run outputs.")

    # --- Observability ------------------------------------------------------
    log_level: LogLevel = Field(default="INFO", description="Root log level.")

    @property
    def has_anthropic_key(self) -> bool:
        """True when a non-empty API key is configured."""
        return bool(self.anthropic_api_key and self.anthropic_api_key.get_secret_value())


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return the process-wide settings instance (cached after first load)."""
    return Settings()
