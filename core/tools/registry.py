"""Tool registry for handler lookup and registration."""
from __future__ import annotations

from typing import Any, Callable, Dict

from core.config.runtime import get_runtime_config

Handler = Callable[..., Any]


class ToolRegistry:
    """Registry for tool handlers."""

    def __init__(self, allow_overwrite: bool | None = None) -> None:
        runtime = get_runtime_config()
        self._allow_overwrite = (
            runtime.allow_tool_overwrite
            if allow_overwrite is None
            else allow_overwrite
        )
        self._handlers: Dict[str, Handler] = {}

    @property
    def allow_overwrite(self) -> bool:
        return self._allow_overwrite

    def register(self, name: str, handler: Handler) -> None:
        """Register a tool handler.

        If allow_overwrite is False, attempting to register a duplicate name
        raises a ValueError. If allow_overwrite is True, the handler is replaced.
        """
        if not self._allow_overwrite and name in self._handlers:
            raise ValueError(f"Tool '{name}' is already registered")
        self._handlers[name] = handler

    def get(self, name: str) -> Handler:
        """Return a registered handler by name."""
        return self._handlers[name]

    def has(self, name: str) -> bool:
        """Return True if a handler is registered."""
        return name in self._handlers
