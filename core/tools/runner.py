"""Tool runner returning a structured envelope."""
from __future__ import annotations

from typing import Any, Dict, Optional

from core.config.runtime import get_runtime_config
from core.tools.errors import ToolError
from core.tools.registry import ToolRegistry


def run(
    name: str,
    registry: ToolRegistry,
    *args: Any,
    **kwargs: Any,
) -> Dict[str, Any]:
    """Run a registered tool and return a structured envelope."""
    runtime = get_runtime_config()
    run_id = runtime.run_id_factory()
    stage = runtime.default_stage

    envelope: Dict[str, Any] = {
        "ok": False,
        "stage": stage,
        "run_id": run_id,
        "summary": None,
        "result": None,
        "evidence": None,
        "error": None,
    }

    try:
        handler = registry.get(name)
        result = handler(*args, **kwargs)
        envelope.update(
            {
                "ok": True,
                "stage": "completed",
                "summary": "success",
                "result": result,
                "error": None,
            }
        )
    except ToolError as exc:
        envelope.update(
            {
                "ok": False,
                "stage": exc.stage,
                "summary": exc.message,
                "error": exc.to_dict(),
            }
        )
    except Exception as exc:  # noqa: BLE001 - must catch all exceptions
        tool_error = ToolError.from_exception(exc, stage="exception")
        envelope.update(
            {
                "ok": False,
                "stage": tool_error.stage,
                "summary": tool_error.message,
                "error": tool_error.to_dict(),
            }
        )

    return envelope
