"""Run storage helpers for hc agent."""

from __future__ import annotations

import dataclasses
import json
from enum import Enum
from pathlib import Path
from typing import Any


def sanitize_obj(value: Any) -> Any:
    """Return a JSON-serializable structure derived from value."""
    if dataclasses.is_dataclass(value):
        return sanitize_obj(dataclasses.asdict(value))
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, dict):
        return {str(key): sanitize_obj(val) for key, val in value.items()}
    if isinstance(value, (list, tuple, set, frozenset)):
        return [sanitize_obj(item) for item in value]
    return str(value)


def build_min_evidence(evidence: Any) -> Any:
    """Trim evidence payloads down to a minimal summary when possible."""
    if evidence is None:
        return {}
    if isinstance(evidence, dict):
        preferred_keys = (
            "summary",
            "highlights",
            "metrics",
            "files",
            "artifacts",
            "errors",
            "warnings",
            "notes",
        )
        trimmed = {key: evidence[key] for key in preferred_keys if key in evidence}
        return trimmed if trimmed else evidence
    if isinstance(evidence, (list, tuple, set, frozenset)):
        return list(evidence)
    return evidence


def _write_json(path: Path, payload: Any) -> None:
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def init_run_dir(base_dir: Path | str, run_id: str) -> Path:
    run_dir = Path(base_dir) / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    return run_dir


def write_run_artifacts(
    *,
    base_dir: Path | str,
    run_id: str,
    preview: Any,
    apply: Any,
    evidence: Any,
    run: Any,
    report_md: str,
) -> Path:
    run_dir = init_run_dir(base_dir, run_id)

    _write_json(run_dir / "preview.json", sanitize_obj(preview))
    _write_json(run_dir / "apply.json", sanitize_obj(apply))
    _write_json(
        run_dir / "evidence.json", sanitize_obj(build_min_evidence(evidence))
    )
    _write_json(run_dir / "run.json", sanitize_obj(run))

    (run_dir / "report.md").write_text(report_md, encoding="utf-8")
    return run_dir
