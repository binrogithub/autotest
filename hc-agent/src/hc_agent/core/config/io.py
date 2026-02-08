"""
Configuration I/O utilities.
"""
from __future__ import annotations

import os
from typing import Any, Dict


def load_yaml_if_exists(path: str) -> Dict[str, Any]:
    """
    Load a YAML file if it exists.

    Returns an empty dictionary if the file does not exist
    or cannot be parsed.
    """
    if not path:
        return {}

    if not os.path.exists(path):
        return {}

    try:
        import yaml

        with open(path, "r", encoding="utf-8") as handle:
            data = yaml.safe_load(handle)
            return data if isinstance(data, dict) else {}
    except Exception:
        return {}
