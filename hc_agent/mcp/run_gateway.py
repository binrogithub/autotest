from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


SENSITIVE_KEYS = {
    "api_key",
    "apikey",
    "authorization",
    "auth",
    "token",
    "secret",
    "password",
    "passwd",
}

EVIDENCE_WHITELIST = {
    "id",
    "type",
    "path",
    "url",
    "title",
    "summary",
    "details",
    "timestamp",
    "metadata",
}


def _sanitize_payload(payload: Any) -> Any:
    if isinstance(payload, dict):
        sanitized: dict[str, Any] = {}
        for key, value in payload.items():
            if key.lower() in SENSITIVE_KEYS:
                sanitized[key] = "[redacted]"
            else:
                sanitized[key] = _sanitize_payload(value)
        return sanitized
    if isinstance(payload, list):
        return [_sanitize_payload(item) for item in payload]
    return payload


def _whitelist_evidence(evidence: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    whitelisted: list[dict[str, Any]] = []
    for entry in evidence:
        if not isinstance(entry, dict):
            continue
        filtered = {key: _sanitize_payload(value) for key, value in entry.items() if key in EVIDENCE_WHITELIST}
        whitelisted.append(filtered)
    return whitelisted


@dataclass(frozen=True)
class RunStore:
    run_id: str
    base_dir: Path = Path("runs")

    def __post_init__(self) -> None:
        run_dir = self.run_dir
        run_dir.mkdir(parents=True, exist_ok=True)

    @property
    def run_dir(self) -> Path:
        return self.base_dir / self.run_id

    def write_preview(self, preview: dict[str, Any]) -> Path:
        return self._write_json("preview.json", preview)

    def write_apply(self, apply_payload: dict[str, Any]) -> Path:
        return self._write_json("apply.json", apply_payload)

    def write_run(self, run: dict[str, Any]) -> Path:
        return self._write_json("run.json", run)

    def write_evidence(self, evidence: Iterable[dict[str, Any]]) -> Path:
        sanitized = _whitelist_evidence(evidence)
        return self._write_json("evidence.json", sanitized)

    def write_report(self, report_md: str) -> Path:
        path = self.run_dir / "report.md"
        path.write_text(report_md, encoding="utf-8")
        return path

    def _write_json(self, filename: str, payload: Any) -> Path:
        path = self.run_dir / filename
        sanitized = _sanitize_payload(payload)
        path.write_text(json.dumps(sanitized, indent=2, sort_keys=True), encoding="utf-8")
        return path


def hc_run(
    *,
    run_id: str,
    preview: dict[str, Any],
    apply: dict[str, Any],
    run: dict[str, Any],
    evidence: Iterable[dict[str, Any]],
    report_md: str,
    base_dir: str | os.PathLike[str] = "runs",
) -> dict[str, str]:
    store = RunStore(run_id=run_id, base_dir=Path(base_dir))
    store.write_preview(preview)
    store.write_apply(apply)
    store.write_run(run)
    store.write_evidence(evidence)
    store.write_report(report_md)
    return {
        "run_id": run_id,
        "run_dir": str(store.run_dir),
    }


def hc_run_demo(base_dir: str | os.PathLike[str] = "runs") -> dict[str, str]:
    run_id = datetime.now(timezone.utc).strftime("demo-%Y%m%d-%H%M%S")
    preview = {
        "title": "Demo run",
        "requested_by": "hc_run_demo",
    }
    apply = {
        "steps": [
            {"action": "collect", "target": "demo"},
        ],
    }
    run = {
        "status": "completed",
        "duration_s": 0,
    }
    evidence = [
        {"id": "demo-1", "type": "note", "summary": "Demo evidence entry."},
    ]
    report_md = "# Demo Report\n\nThis is a demo run report."
    return hc_run(
        run_id=run_id,
        preview=preview,
        apply=apply,
        run=run,
        evidence=evidence,
        report_md=report_md,
        base_dir=base_dir,
    )
