"""Handlers for hc agent commands."""

from __future__ import annotations

from typing import Any, Dict, List, Mapping, Optional

from hc_agent.core import doctor


class HandlerResult(dict):
    """Simple result wrapper to standardize handler responses."""


def hc_doctor_fix(context: Mapping[str, Any], missing: Optional[List[str]] = None) -> HandlerResult:
    """Fill missing values using defaults or agent selection."""
    values: Dict[str, Any] = dict(context.get("values") or {})
    defaults: Dict[str, Any] = dict(context.get("defaults") or {})

    missing_keys = missing or _find_missing(values, context.get("required") or [])
    for key in missing_keys:
        if key in defaults:
            values[key] = defaults[key]

    if "agent" in missing_keys and "agent" not in values:
        agents = context.get("agents") or []
        explicit = context.get("explicit_agent")
        config = context.get("config_agent")
        selected = doctor.select_agent(agents, explicit=explicit, config=config)
        if selected is not None:
            values["agent"] = selected

    return HandlerResult(status="fixed", values=values)


def hc_run_demo(context: Mapping[str, Any]) -> HandlerResult:
    """Run the demo, auto-invoking doctor fix in non-interactive mode."""
    values: Dict[str, Any] = dict(context.get("values") or {})
    required = list(context.get("required") or [])
    missing = _find_missing(values, required)

    if missing:
        if context.get("non_interactive"):
            fix_result = hc_doctor_fix(context, missing=missing)
            values = dict(fix_result.get("values") or {})
            missing = _find_missing(values, required)
            if missing:
                return HandlerResult(status="error", missing=missing)
            return HandlerResult(status="ok", values=values, auto_invoked="hc_doctor_fix")
        return HandlerResult(status="needs_input", missing=missing)

    return HandlerResult(status="ok", values=values)


def _find_missing(values: Mapping[str, Any], required: List[str]) -> List[str]:
    missing = []
    for key in required:
        if values.get(key) in (None, ""):
            missing.append(key)
    return missing


HANDLERS = {
    "hc_doctor_fix": hc_doctor_fix,
    "hc_run_demo": hc_run_demo,
}
