"""Run configuration: one YAML file in ``configs/`` describes a full pipeline.

A run config bundles retrieval, generation and judge settings so that
``rag query`` and ``rag eval run`` read the same file and an experiment run can
snapshot exactly what it used. Model names left as ``null`` fall back to
:class:`~ragplatform.config.Settings` at run time.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import yaml
from pydantic import BaseModel, ConfigDict, Field

from ragplatform.retrieval.config import RetrievalConfig

if TYPE_CHECKING:
    from pathlib import Path


class GenerationConfig(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    prompt_version: str = Field(default="answer_v1", description="File in ragplatform/prompts.")
    model: str | None = Field(default=None, description="Overrides Settings.anthropic_model.")
    max_tokens: int = Field(default=4096, ge=1)


class JudgeConfig(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    model: str | None = Field(default=None, description="Overrides Settings.anthropic_judge_model.")
    faithfulness_prompt: str = "judge_faithfulness_v1"
    correctness_prompt: str = "judge_correctness_v1"
    relevance_prompt: str = "judge_relevance_v1"
    max_tokens: int = Field(default=4096, ge=1)


class RunConfig(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    name: str = Field(min_length=1)
    retrieval: RetrievalConfig = Field(default_factory=RetrievalConfig)
    generation: GenerationConfig = Field(default_factory=GenerationConfig)
    judge: JudgeConfig = Field(default_factory=JudgeConfig)


def load_run_config(path: Path) -> RunConfig:
    """Parse a YAML run config; ``name`` defaults to the file stem."""
    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(raw, dict):
        raise ValueError(f"{path}: top level must be a mapping")
    raw.setdefault("name", path.stem)
    return RunConfig.model_validate(raw)
