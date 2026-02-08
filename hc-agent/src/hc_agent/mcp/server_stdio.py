"""
MCP server using stdio transport.

This module enables hc-agent to communicate with AI agents
over standard input/output.
"""

from __future__ import annotations

import json
import sys

from hc_agent.mcp.server_core import McpServer


def serve_stdio(server: McpServer) -> None:
    """
    Start an MCP server over stdio.
    """
    for line in sys.stdin:
        try:
            request = json.loads(line)
            method = request.get("method")
            params = request.get("params", {})

            if method == "list_tools":
                result = server.list_tools()
            elif method == "run_tool":
                result = server.run_tool(**params)
            else:
                result = {"error": f"Unknown method: {method}"}

            response = {"result": result}
        except Exception as exc:
            response = {"error": str(exc)}

        sys.stdout.write(json.dumps(response) + "\n")
        sys.stdout.flush()
