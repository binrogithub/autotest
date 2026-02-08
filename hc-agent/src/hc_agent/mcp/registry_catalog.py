"""
Tool catalog builder for MCP discovery.
"""

from __future__ import annotations

from typing import Any, Dict, List

from hc_agent.core.tools.registry import ToolRegistry


def build_catalog() -> List[Dict[str, Any]]:
    """
    Build a searchable catalog of tools.
    """
    catalog = []
    for name in ToolRegistry.list_tools():
        schema = ToolRegistry.schema(name)
        catalog.append(
            {
                "name": name,
                "description": schema.get("doc", ""),
                "risk": "write",
            }
        )
    return catalog
