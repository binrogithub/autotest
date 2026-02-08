"""Gateway for hc agent runs."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from .storage import write_run_artifacts


@dataclass(frozen=True)
class RunRequest:
    preview: Any
    apply: Any
    evidence: Any
    run: Any
    report_md: str
    run_id: str = field(default_factory=lambda: uuid4().hex)


@dataclass(frozen=True)
class RunResult:
    run_id: str
    run_dir: str
    stored_at: str


def hc_run(request: RunRequest, *, base_dir: str = "runs") -> RunResult:
    """Persist run artifacts and return storage metadata."""
    run_dir = write_run_artifacts(
        base_dir=base_dir,
        run_id=request.run_id,
        preview=request.preview,
        apply=request.apply,
        evidence=request.evidence,
        run=request.run,
        report_md=request.report_md,
    )
    stored_at = datetime.now(timezone.utc).isoformat()
    return RunResult(run_id=request.run_id, run_dir=str(run_dir), stored_at=stored_at)


def hc_run_demo(*, base_dir: str = "runs") -> RunResult:
    """Create a demo run with placeholder data."""
    request = RunRequest(
        preview={"summary": "Demo preview", "steps": ["analyze", "plan"]},
        apply={"summary": "Demo apply", "steps": ["execute", "verify"]},
        evidence={"summary": "Demo evidence", "artifacts": ["log.txt"]},
        run={"status": "demo", "metadata": {"source": "hc_run_demo"}},
        report_md="# Demo Report\n\nThis is a demo report.",
    )
    return hc_run(request, base_dir=base_dir)
