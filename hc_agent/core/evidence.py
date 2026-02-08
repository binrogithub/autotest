"""Evidence filtering helpers."""

from __future__ import annotations

from typing import Mapping

ALLOWED_EVIDENCE_KEYS: tuple[str, ...] = (
    "service",
    "endpoint",
    "method",
    "path",
    "status",
    "request_id",
    "duration_ms",
    "signature_sha256",
)


def build_min_evidence(evidence: Mapping[str, object] | None) -> dict[str, object]:
    """Return a minimal evidence payload containing only allowed keys."""
    if not evidence:
        return {}

    return {
        key: evidence[key]
        for key in ALLOWED_EVIDENCE_KEYS
        if key in evidence
    }

