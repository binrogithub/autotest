"""Handlers for MCP tool discovery."""

from __future__ import annotations

from typing import Any

from hc_agent.core.tool_registry import ToolRegistry


def hc_tools_search() -> list[dict[str, Any]]:
    """Return the tool catalog for MCP tool discovery."""
    catalog = ToolRegistry.schema()
    return [
        {
            "name": tool["name"],
            "description": tool["description"],
            "risk": tool["risk"],
            "input_schema": tool["input_schema"],
            "output_schema": tool["output_schema"],
            "examples": tool["examples"],
        }
        for tool in catalog
    ]
