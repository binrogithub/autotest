"""Errors raised during tool execution."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass
class ToolError(Exception):
    """Structured tool error with serialization support."""

    message: str
    stage: str = "error"
    details: Dict[str, Any] = field(default_factory=dict)

    def __str__(self) -> str:
        return self.message

    def to_dict(self) -> Dict[str, Any]:
        """Serialize the error for the runner envelope."""
        return {
            "message": self.message,
            "stage": self.stage,
            "details": self.details,
        }

    @classmethod
    def from_exception(
        cls, exc: BaseException, stage: Optional[str] = None
    ) -> "ToolError":
        """Wrap an unexpected exception into a ToolError."""
        return cls(
            message=str(exc) or exc.__class__.__name__,
            stage=stage or "error",
            details={"type": exc.__class__.__name__},
        )
