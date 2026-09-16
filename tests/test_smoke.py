"""Smoke tests: the package imports and exposes its public surface."""

from __future__ import annotations

import importlib

import ragplatform

SUBPACKAGES = (
    "ingestion",
    "retrieval",
    "agent",
    "llm",
    "evals",
    "data_quality",
    "pipelines",
    "api",
    "observability",
)


def test_version_is_set() -> None:
    assert ragplatform.__version__ == "0.1.0"


def test_public_names_are_exported() -> None:
    for name in ragplatform.__all__:
        assert hasattr(ragplatform, name), name


def test_all_subpackages_import() -> None:
    for name in SUBPACKAGES:
        module = importlib.import_module(f"ragplatform.{name}")
        assert module.__doc__, f"ragplatform.{name} should document its responsibility"
