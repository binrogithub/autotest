"""
Automatic parameter resolution.
"""

from __future__ import annotations

from typing import Any, Dict


def doctor_fix(ctx, args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Resolve missing parameters deterministically.
    """
    _ = ctx
    patch: Dict[str, Any] = {}

    for key, value in args.items():
        if value is None:
            patch[key] = "<auto-resolved>"

    return {
        "ok": True,
        "ctx_patch": patch,
    }
