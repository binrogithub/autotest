"""
Network service handler.
"""

from __future__ import annotations

from typing import Any, Dict


def create_security_group(
    *,
    mode: str,
    args: Dict[str, Any],
    ctx,
    run_id: str | None = None,
) -> Dict[str, Any]:
    """
    Create a security group.
    """
    _ = (args, ctx, run_id)
    if mode == "preview":
        return {
            "summary": "Would create security group.",
            "result": {"api_preview": "Security group create request"},
            "evidence": {"service": "vpc"},
        }

    return {
        "summary": "Security group created.",
        "result": {"resource_ids": ["sg-xxxx"]},
        "evidence": {"service": "vpc"},
    }
