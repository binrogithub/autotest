"""Utilities for redacting sensitive data."""

from __future__ import annotations

import hashlib
from typing import Any

SENSITIVE_KEY_FRAGMENTS = (
    "token",
    "secret",
    "cert",
    "kubeconfig",
)

LARGE_STRING_THRESHOLD = 128


def _is_sensitive_key(key: Any) -> bool:
    if not isinstance(key, str):
        return False
    lowered = key.lower()
    return any(fragment in lowered for fragment in SENSITIVE_KEY_FRAGMENTS)


def _redacted_value(value: Any) -> str:
    if isinstance(value, bytes):
        digest = hashlib.sha256(value).hexdigest()
        length = len(value)
        return f"<redacted sha256={digest} len={length}>"
    if isinstance(value, str):
        digest = hashlib.sha256(value.encode("utf-8", "replace")).hexdigest()
        length = len(value)
        return f"<redacted sha256={digest} len={length}>"
    return "<redacted>"


def sanitize_obj(obj: Any) -> Any:
    """Return a sanitized copy of nested data structures.

    Redacts sensitive keys and large strings while preserving structure.
    """
    if isinstance(obj, dict):
        sanitized: dict[Any, Any] = {}
        for key, value in obj.items():
            if _is_sensitive_key(key):
                sanitized[key] = _redacted_value(value)
            else:
                sanitized[key] = sanitize_obj(value)
        return sanitized
    if isinstance(obj, list):
        return [sanitize_obj(item) for item in obj]
    if isinstance(obj, tuple):
        return tuple(sanitize_obj(item) for item in obj)
    if isinstance(obj, set):
        return {sanitize_obj(item) for item in obj}
    if isinstance(obj, bytes):
        if len(obj) > LARGE_STRING_THRESHOLD:
            return _redacted_value(obj)
        return obj
    if isinstance(obj, str):
        if len(obj) > LARGE_STRING_THRESHOLD:
            return _redacted_value(obj)
        return obj
    return obj
