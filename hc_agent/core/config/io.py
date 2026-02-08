"""Configuration IO helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Any


def load_yaml_if_exists(path: str | Path) -> dict[str, Any]:
    """Load a YAML file if it exists, returning an empty dict otherwise."""
    candidate = Path(path)
    if not candidate.exists():
        return {}

    import yaml

    with candidate.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}
