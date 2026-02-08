"""
Recursive data sanitization utilities.
"""

from __future__ import annotations

import hashlib
from typing import Any


SENSITIVE_KEYS = {
    "access_key",
    "secret_key",
    "token",
    "authorization",
    "x-auth-token",
    "password",
    "private_key",
    "certificate",
    "kubeconfig",
}


def _hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8", errors="ignore")).hexdigest()


def sanitize_obj(obj: Any) -> Any:
    """
    Recursively sanitize sensitive fields in dictionaries and lists.
    """
    if isinstance(obj, dict):
        result = {}
        for k, v in obj.items():
            if k.lower() in SENSITIVE_KEYS:
                result[k] = f"<redacted:{_hash(str(v))}>"
            else:
                result[k] = sanitize_obj(v)
        return result

    if isinstance(obj, list):
        return [sanitize_obj(i) for i in obj]

    return obj
