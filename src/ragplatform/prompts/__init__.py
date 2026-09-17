"""Versioned prompt files.

Every prompt lives in this package as ``<name>_v<N>.txt`` and is referenced by
that name (``answer_v1``) in configs and recorded in every output, so a result
can always be traced to the exact prompt text that produced it. Editing a
prompt means creating a new version, not changing an old file.
"""

from __future__ import annotations

from importlib import resources

_PACKAGE = "ragplatform.prompts"


def load_prompt(name: str) -> str:
    """Return the text of ``<name>.txt`` from this package."""
    resource = resources.files(_PACKAGE) / f"{name}.txt"
    if not resource.is_file():
        raise FileNotFoundError(f"prompt {name!r} not found in {_PACKAGE}")
    return resource.read_text(encoding="utf-8")


def list_prompts() -> list[str]:
    return sorted(
        entry.name[:-4]
        for entry in resources.files(_PACKAGE).iterdir()
        if entry.name.endswith(".txt")
    )
