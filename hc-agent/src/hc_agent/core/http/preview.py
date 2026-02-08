"""
API request preview generation.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any, Dict


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", errors="ignore")).hexdigest()


def build_api_preview(spec) -> Dict[str, Any]:
    """
    Build a redacted preview of an API request.
    """
    preview = {
        "service": spec.service,
        "method": spec.method,
        "endpoint": spec.endpoint,
        "path": spec.path,
        "query": spec.query or {},
        "headers": {
            k: v
            for k, v in (spec.headers or {}).items()
            if k.lower() not in ("authorization", "x-auth-token")
        },
        "json_body": spec.json_body or {},
    }

    preview_str = json.dumps(preview, sort_keys=True, ensure_ascii=False)
    preview["preview_sha256"] = _sha256(preview_str)
    return preview
