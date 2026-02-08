"""
Compute service handler.
"""

from __future__ import annotations

from typing import Any, Dict

from hc_agent.core.tools.errors import ToolError


def create_ecs(*, mode: str, args: Dict[str, Any], ctx, run_id: str | None = None) -> Dict[str, Any]:
    """
    Create an ECS instance.
    """
    _ = (args, run_id)
    if not ctx.project_id:
        raise ToolError(
            code="project_id_missing",
            summary="Project ID is required for ECS operations.",
            fix=["Set context.project_id in config.yaml or HC_PROJECT_ID env var."],
        )

    if mode == "preview":
        return {
            "summary": "Would create ECS instance.",
            "result": {"api_preview": "ECS create request"},
            "evidence": {"service": "ecs"},
        }

    return {
        "summary": "ECS instance created.",
        "result": {"resource_ids": ["ecs-xxxx"]},
        "evidence": {"service": "ecs"},
    }
