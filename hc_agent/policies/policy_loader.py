"""Policy loader helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Any


def load_policy_file(path: str | Path) -> dict[str, Any]:
    """Load a policy YAML file and return the parsed data."""
    import yaml

    with Path(path).open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}
