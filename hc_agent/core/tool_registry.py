"""Registry for tool schemas used by hc_agent."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Iterable
import copy


@dataclass(frozen=True)
class ToolSpec:
    name: str
    description: str
    risk: str
    input_schema: dict[str, Any]
    output_schema: dict[str, Any]
    examples: tuple[dict[str, Any], ...] = ()


class ToolRegistry:
    """Central registry for tool schemas.

    Tool specifications should be added here to avoid duplicate definitions.
    """

    _tools: list[ToolSpec] = []

    @classmethod
    def register(cls, tool: ToolSpec) -> None:
        cls._tools.append(tool)

    @classmethod
    def schema(cls) -> tuple[dict[str, Any], ...]:
        """Return a deterministic catalog of tool schemas."""
        tools = sorted(cls._tools, key=lambda tool: tool.name)
        return tuple(cls._serialize(tool) for tool in tools)

    @staticmethod
    def _serialize(tool: ToolSpec) -> dict[str, Any]:
        data = asdict(tool)
        data["examples"] = list(tool.examples)
        return copy.deepcopy(data)


__all__: Iterable[str] = ["ToolRegistry", "ToolSpec"]
