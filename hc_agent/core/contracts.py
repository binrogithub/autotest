"""Shared contracts for runner payloads and summaries."""

from __future__ import annotations

from typing import Any, Dict, Optional, TypedDict


class StructuredError(TypedDict, total=False):
    """Structured error details used in runner payloads."""

    type: str
    message: str
    details: Dict[str, Any]


def build_structured_error(
    error_type: str,
    message: str,
    details: Optional[Dict[str, Any]] = None,
) -> StructuredError:
    """Build a StructuredError dictionary with stable JSON field names."""

    payload: StructuredError = {
        "type": error_type,
        "message": message,
    }
    if details is not None:
        payload["details"] = details
    return payload


class RunSummary(TypedDict, total=False):
    """Summary payload for a completed run."""

    status: str
    started_at: str
    finished_at: str
    duration_ms: int
    metadata: Dict[str, Any]


class RunnerEnvelope(TypedDict, total=False):
    """Envelope payload for runner communication."""

    run_id: str
    summary: RunSummary
    error: StructuredError
    metadata: Dict[str, Any]
