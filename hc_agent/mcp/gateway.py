"""Gateway layer for MCP tool routing."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, Iterable, List, Mapping, Tuple


@dataclass(frozen=True)
class ToolSpec:
    name: str
    description: str
    input_schema: Mapping[str, Any]

    def as_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "inputSchema": dict(self.input_schema),
        }


ToolHandler = Callable[[Mapping[str, Any]], Dict[str, Any]]


def _text_response(message: str, **payload: Any) -> Dict[str, Any]:
    response = {
        "status": "ok",
        "message": message,
    }
    response.update(payload)
    return response


def _hc_tools_search(arguments: Mapping[str, Any]) -> Dict[str, Any]:
    query = str(arguments.get("query", "")).strip().lower()
    if not query:
        matches = [spec.name for spec in _TOOL_SPECS]
    else:
        matches = [
            spec.name
            for spec in _TOOL_SPECS
            if query in spec.name.lower() or query in spec.description.lower()
        ]
    return _text_response("Tool search results.", matches=matches)


def _hc_run(arguments: Mapping[str, Any]) -> Dict[str, Any]:
    command = str(arguments.get("command", "")).strip()
    if not command:
        return _text_response("No command provided.", executed=False)
    return _text_response("Command captured for execution.", executed=False, command=command)


def _hc_run_demo(arguments: Mapping[str, Any]) -> Dict[str, Any]:
    scenario = str(arguments.get("scenario", "demo")).strip() or "demo"
    return _text_response("Demo run prepared.", scenario=scenario)


def _hc_doctor_fix(arguments: Mapping[str, Any]) -> Dict[str, Any]:
    issue = str(arguments.get("issue", "")).strip()
    if not issue:
        return _text_response("No issues detected.", actions=[])
    return _text_response("Suggested fix prepared.", actions=[f"Review issue: {issue}"])


_TOOL_SPECS: Tuple[ToolSpec, ...] = (
    ToolSpec(
        name="hc_tools_search",
        description="Search available hc tools by name or description.",
        input_schema={
            "type": "object",
            "properties": {"query": {"type": "string"}},
            "additionalProperties": False,
        },
    ),
    ToolSpec(
        name="hc_run",
        description="Capture a command invocation request.",
        input_schema={
            "type": "object",
            "properties": {"command": {"type": "string"}},
            "required": ["command"],
            "additionalProperties": False,
        },
    ),
    ToolSpec(
        name="hc_run_demo",
        description="Prepare a demo run for the hc toolchain.",
        input_schema={
            "type": "object",
            "properties": {"scenario": {"type": "string"}},
            "additionalProperties": False,
        },
    ),
    ToolSpec(
        name="hc_doctor_fix",
        description="Suggest remediation steps for an issue.",
        input_schema={
            "type": "object",
            "properties": {"issue": {"type": "string"}},
            "additionalProperties": False,
        },
    ),
)

_TOOL_HANDLERS: Dict[str, ToolHandler] = {
    "hc_tools_search": _hc_tools_search,
    "hc_run": _hc_run,
    "hc_run_demo": _hc_run_demo,
    "hc_doctor_fix": _hc_doctor_fix,
}


def list_tool_specs() -> Tuple[ToolSpec, ...]:
    """Return the stable catalog of registered tools."""
    return _TOOL_SPECS


def list_tools() -> List[Dict[str, Any]]:
    """Return tool specs as serializable dictionaries."""
    return [spec.as_dict() for spec in _TOOL_SPECS]


def call_tool(name: str, arguments: Mapping[str, Any] | None = None) -> Dict[str, Any]:
    if arguments is None:
        arguments = {}
    handler = _TOOL_HANDLERS.get(name)
    if handler is None:
        return {
            "status": "error",
            "message": f"Unknown tool: {name}",
        }
    return handler(arguments)
