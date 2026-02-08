"""
Structured error definitions for tools.
"""

from __future__ import annotations

from typing import List, Optional


class ToolError(Exception):
    """
    Structured error raised by tools and handlers.
    """

    def __init__(
        self,
        *,
        code: str,
        summary: str,
        details: Optional[str] = None,
        fix: Optional[List[str]] = None,
    ) -> None:
        super().__init__(summary)
        self.code = code
        self.summary = summary
        self.details = details
        self.fix = fix or []

    def to_dict(self) -> dict:
        return {
            "code": self.code,
            "summary": self.summary,
            "details": self.details,
            "fix": self.fix,
        }
