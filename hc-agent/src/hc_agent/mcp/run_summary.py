"""
Run summary builder.
"""

from __future__ import annotations

from typing import Any, Dict


def build_run_summary(
    *,
    run_id: str,
    stage: str,
    summary: str,
    result: Dict[str, Any] | None,
    error: Dict[str, Any] | None,
) -> Dict[str, Any]:
    """
    Build a standardized run summary document.
    """
    return {
        "run_id": run_id,
        "stage": stage,
        "summary": summary,
        "result": result,
        "error": error,
        "uri": f"hc-run://{run_id}/run.json",
    }
