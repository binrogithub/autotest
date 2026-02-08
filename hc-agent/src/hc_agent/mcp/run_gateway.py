"""
Execution gateway for hc_run and hc_run_demo.
"""

from __future__ import annotations

import uuid
from typing import Any, Dict

from hc_agent.core.tools.runner import run as run_tool
from hc_agent.mcp.run_summary import build_run_summary
from hc_agent.mcp.state_store import RunStore

store = RunStore()


def hc_run(
    *,
    tool_name: str,
    mode: str,
    args: Dict[str, Any],
    ctx,
    run_id: str | None = None,
) -> Dict[str, Any]:
    """
    Execute a single tool through the gateway.
    """
    rid = run_id or f"RUN-{uuid.uuid4().hex[:8]}"
    store.init_run(rid)

    result = run_tool(
        tool_name=tool_name,
        mode=mode,
        args=args,
        ctx=ctx,
        run_id=rid,
    )

    store.write_json(rid, mode, result)

    return build_run_summary(
        run_id=rid,
        stage=mode,
        summary=result.get("summary"),
        result=result.get("result"),
        error=result.get("error"),
    )
