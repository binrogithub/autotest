"""
Storage service handler.
"""

from __future__ import annotations

from typing import Any, Dict


def create_bucket(*, mode: str, args: Dict[str, Any], ctx, run_id: str | None = None) -> Dict[str, Any]:
    """
    Create an OBS bucket.
    """
    _ = (args, ctx, run_id)
    if mode == "preview":
        return {
            "summary": "Would create OBS bucket.",
            "result": {"api_preview": "OBS create bucket request"},
            "evidence": {"service": "obs"},
        }

    return {
        "summary": "OBS bucket created.",
        "result": {"resource_ids": ["bucket-xxxx"]},
        "evidence": {"service": "obs"},
    }
