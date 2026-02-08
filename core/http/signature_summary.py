"""Helpers to summarize signature data for preview outputs."""

from __future__ import annotations

import hashlib
from typing import Any, Mapping


def _hash_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def build_signature_summary(
    signed_headers: Mapping[str, str],
    canonical_request: str,
    string_to_sign: str,
) -> dict[str, Any]:
    signature_hash = signed_headers.get("x-signature") or _hash_text(string_to_sign)
    return {
        "signed_headers": dict(signed_headers),
        "canonical_request": canonical_request,
        "string_to_sign": string_to_sign,
        "signature_hash": signature_hash,
    }


def format_signature_summary(summary: Mapping[str, Any]) -> str:
    return (
        "Signature Summary\n"
        f"Signed headers: {sorted(summary.get('signed_headers', {}))}\n"
        f"Signature hash: {summary.get('signature_hash')}"
    )
