"""Run gateway helpers for hc_agent demo flows."""

from __future__ import annotations

import json
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Iterable


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def _render_report(run_dir: Path, run_data: dict) -> str:
    status = run_data["status"]
    mode = run_data["mode"]
    steps = run_data["steps"]
    lines = [
        "# hc_run Demo Report",
        "",
        f"- Status: **{status}**",
        f"- Mode: **{mode}**",
        f"- Started: `{run_data['started_at']}`",
        f"- Ended: `{run_data['ended_at']}`",
        "",
        "## Steps",
    ]
    for step in steps:
        lines.append(
            f"- {step['index']:02d} `{step['group']}`: **{step['status']}**"
        )
    lines.extend(
        [
            "",
            "## Next apply command",
            f"`hc-run --mode apply --run-dir {run_dir}`",
            "",
            "(Update the command to match your local CLI wrapper if needed.)",
        ]
    )
    return "\n".join(lines) + "\n"


def hc_run_demo(
    hc_run: Callable[..., dict],
    run_dir: Path | str,
    mode: str,
    steps: Iterable[str] | None = None,
) -> dict:
    """Run the demo sequence, persisting step artifacts and reports.

    Args:
        hc_run: Callable that executes a step. It must accept group= and mode=.
        run_dir: Directory to persist artifacts into.
        mode: The execution mode (for example, plan/apply).
        steps: Optional iterable of step group names.
    """
    resolved_dir = Path(run_dir)
    resolved_steps = list(steps or ["network", "storage", "compute"])
    run_data: dict = {
        "mode": mode,
        "status": "success",
        "started_at": _now_iso(),
        "ended_at": None,
        "steps": [],
    }
    steps_dir = resolved_dir / "steps"

    for index, group in enumerate(resolved_steps, start=1):
        step_payload = {
            "group": group,
            "index": index,
            "mode": mode,
            "status": "success",
            "started_at": _now_iso(),
        }
        try:
            result = hc_run(group=group, mode=mode)
            step_payload["result"] = result
        except Exception as exc:  # pragma: no cover - defensive runtime guard
            step_payload["status"] = "error"
            step_payload["error"] = str(exc)
            step_payload["traceback"] = traceback.format_exc()
            run_data["status"] = "error"
        step_payload["ended_at"] = _now_iso()

        step_path = steps_dir / f"{index:02d}-{group}.{mode}.json"
        _write_json(step_path, step_payload)

        run_data["steps"].append(
            {
                "group": group,
                "index": index,
                "mode": mode,
                "status": step_payload["status"],
                "artifact": step_path.relative_to(resolved_dir).as_posix(),
            }
        )

        if step_payload["status"] == "error":
            break

    run_data["ended_at"] = _now_iso()
    _write_json(resolved_dir / "run.json", run_data)

    report_path = resolved_dir / "report.md"
    report_path.write_text(_render_report(resolved_dir, run_data))

    return run_data
