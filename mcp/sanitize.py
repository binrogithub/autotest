"""Sanitize run output before persistence.

Example:
    sanitized = sanitize_value({"log": "hello\x00world"})
"""

import re

_CONTROL_CHARS = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")


def _sanitize_string(value):
    return _CONTROL_CHARS.sub("", value)


def sanitize_value(value):
    """Recursively sanitize values for storage and reporting."""
    if value is None:
        return None
    if isinstance(value, (bool, int, float)):
        return value
    if isinstance(value, bytes):
        return _sanitize_string(value.decode("utf-8", errors="replace"))
    if isinstance(value, str):
        return _sanitize_string(value)
    if isinstance(value, dict):
        return {str(key): sanitize_value(val) for key, val in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [sanitize_value(item) for item in value]
    return _sanitize_string(str(value))
