"""
Human-readable report rendering.
"""

from __future__ import annotations

from typing import Any, Dict


def render_report_md(run: Dict[str, Any]) -> str:
    """
    Render a Markdown report for a run.
    """
    lines = [
        f"# Run Report: {run.get('run_id')}",
        "",
        f"**Stage:** {run.get('stage')}",
        "",
        f"**Summary:** {run.get('summary')}",
        "",
    ]

    if run.get("error"):
        lines.append("## Error")
        lines.append("```json")
        lines.append(str(run["error"]))
        lines.append("```")
    else:
        lines.append("## Result")
        lines.append("```json")
        lines.append(str(run.get("result")))
        lines.append("```")

    return "\n".join(lines)
