"""
MCP server using HTTP transport.

This module exposes MCP endpoints over HTTP using FastAPI.
"""

from __future__ import annotations

from importlib.util import find_spec

if find_spec("fastapi") and find_spec("pydantic"):
    from typing import Any, Dict

    from fastapi import FastAPI, HTTPException
    from pydantic import BaseModel

    from hc_agent.mcp.server_core import McpServer

    app = FastAPI(title="hc-agent MCP Server")
    server = McpServer()


    class RunToolRequest(BaseModel):
        tool_name: str
        mode: str
        args: Dict[str, Any]
        run_id: str | None = None


    @app.get("/tools")
    def list_tools() -> list[dict]:
        """
        List available MCP tools.
        """
        return server.list_tools()


    @app.post("/run")
    def run_tool(req: RunToolRequest) -> dict:
        """
        Execute a tool via MCP over HTTP.
        """
        try:
            # Context injection should be handled by the caller or middleware
            ctx = None
            return server.run_tool(
                tool_name=req.tool_name,
                mode=req.mode,
                args=req.args,
                ctx=ctx,
                run_id=req.run_id,
            )
        except Exception as exc:
            raise HTTPException(status_code=400, detail=str(exc))
else:
    app = None
    server = None
