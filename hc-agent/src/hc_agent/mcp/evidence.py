"""
Minimal execution evidence builder.
"""

from __future__ import annotations

from typing import Any, Dict


EVIDENCE_WHITELIST = {
    "service",
    "endpoint",
    "method",
    "path",
    "status",
    "request_id",
    "duration_ms",
    "signature_sha256",
}


def build_min_evidence(raw: Dict[str, Any]) -> Dict[str, Any]:
    """
    Filter evidence fields using a strict whitelist.
    """
    return {k: v for k, v in raw.items() if k in EVIDENCE_WHITELIST}
