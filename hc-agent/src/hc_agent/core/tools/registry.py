"""
Tool registry implementation.

The registry provides discovery and access to tool handlers.
"""

from __future__ import annotations

from typing import Any, Callable, Dict, List


class ToolRegistry:
    """
    Registry for tool handlers.
    """

    _tools: Dict[str, Callable[..., Any]] = {}

    @classmethod
    def register(cls, name: str, handler: Callable[..., Any]) -> None:
        cls._tools[name] = handler

    @classmethod
    def list_tools(cls) -> List[str]:
        return sorted(cls._tools.keys())

    @classmethod
    def get(cls, name: str) -> Callable[..., Any]:
        if name not in cls._tools:
            raise KeyError(f"Tool not found: {name}")
        return cls._tools[name]

    @classmethod
    def schema(cls, name: str) -> dict:
        """
        Return a minimal schema description for a tool.
        """
        handler = cls.get(name)
        return {
            "name": name,
            "handler": handler.__name__,
            "doc": handler.__doc__ or "",
        }
