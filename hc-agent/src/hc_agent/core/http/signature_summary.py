"""
Signature summary utilities.

Stores only cryptographic hashes of signing material.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any, Dict


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", errors="ignore")).hexdigest()


def build_signature_summary(
    *,
    canonical_request: str,
    signed_headers: Dict[str, Any],
    string_to_sign: str,
) -> Dict[str, str]:
    """
    Build a hash-only summary of request signing material.
    """
    return {
        "canonical_request_sha256": _sha256(canonical_request),
        "string_to_sign_sha256": _sha256(string_to_sign),
        "signed_headers_sha256": _sha256(
            json.dumps(signed_headers, sort_keys=True, ensure_ascii=False)
        ),
    }
