"""MCP server façade for hc_agent tools."""

from __future__ import annotations

from typing import Any, Dict, List, Mapping

from hc_agent.mcp import gateway


class HCMCPServer:
    """Simple MCP server wrapper for hc_agent tool calls."""

    def list_tools(self) -> List[Dict[str, Any]]:
        return gateway.list_tools()

    def call_tool(self, name: str, arguments: Mapping[str, Any] | None = None) -> Dict[str, Any]:
        return gateway.call_tool(name, arguments)


def list_tools() -> List[Dict[str, Any]]:
    """List the registered MCP tools."""
    return gateway.list_tools()


def hc_tools_search(arguments: Mapping[str, Any] | None = None) -> Dict[str, Any]:
    return gateway.call_tool("hc_tools_search", arguments)


def hc_run(arguments: Mapping[str, Any] | None = None) -> Dict[str, Any]:
    return gateway.call_tool("hc_run", arguments)


def hc_run_demo(arguments: Mapping[str, Any] | None = None) -> Dict[str, Any]:
    return gateway.call_tool("hc_run_demo", arguments)


def hc_doctor_fix(arguments: Mapping[str, Any] | None = None) -> Dict[str, Any]:
    return gateway.call_tool("hc_doctor_fix", arguments)


__all__ = [
    "HCMCPServer",
    "hc_doctor_fix",
    "hc_run",
    "hc_run_demo",
    "hc_tools_search",
    "list_tools",
]
