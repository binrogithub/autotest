"""
Core MCP server implementation.

This module defines the logical MCP server that exposes tools,
dispatches execution requests, and provides access to run resources.
"""

from __future__ import annotations

from typing import Any, Dict, List

from hc_agent.core.tools.registry import ToolRegistry
from hc_agent.core.tools.runner import run as run_tool


class McpServer:
    """
    Core MCP server.

    This class is transport-agnostic and can be used by
    stdio or HTTP MCP servers.
    """

    def list_tools(self) -> List[Dict[str, Any]]:
        """
        List available tools with minimal metadata.
        """
        tools = []
        for name in ToolRegistry.list_tools():
            tools.append(ToolRegistry.schema(name))
        return tools

    def run_tool(
        self,
        *,
        tool_name: str,
        mode: str,
        args: Dict[str, Any],
        ctx,
        run_id: str | None = None,
    ) -> Dict[str, Any]:
        """
        Execute a tool through the unified runner.
        """
        return run_tool(
            tool_name=tool_name,
            mode=mode,
            args=args,
            ctx=ctx,
            run_id=run_id,
        )

    def get_resource(self, uri: str) -> Dict[str, Any]:
        """
        Retrieve a run resource by URI.

        This is a placeholder for run store integration.
        """
        raise NotImplementedError("Resource access is not implemented")
