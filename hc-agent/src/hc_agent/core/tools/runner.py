"""
Unified tool runner.

This module executes tools in preview or apply mode and
returns a consistent execution envelope.
"""

from __future__ import annotations

from typing import Any, Dict

from hc_agent.core.tools.errors import ToolError
from hc_agent.core.tools.registry import ToolRegistry


def run(
    *,
    tool_name: str,
    mode: str,
    args: Dict[str, Any],
    ctx,
    run_id: str | None = None,
) -> Dict[str, Any]:
    """
    Run a registered tool and return a standardized envelope.
    """
    try:
        handler = ToolRegistry.get(tool_name)
        payload = handler(
            mode=mode,
            args=args,
            ctx=ctx,
            run_id=run_id,
        )

        return {
            "ok": True,
            "stage": mode,
            "run_id": run_id,
            "summary": payload.get("summary"),
            "result": payload.get("result"),
            "evidence": payload.get("evidence"),
            "error": None,
        }

    except ToolError as err:
        return {
            "ok": False,
            "stage": mode,
            "run_id": run_id,
            "summary": err.summary,
            "result": None,
            "evidence": None,
            "error": err.to_dict(),
        }
