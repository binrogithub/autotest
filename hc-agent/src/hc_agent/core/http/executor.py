"""
HTTP request executor.

Handles preview and apply modes.
"""

from __future__ import annotations

import time
from typing import Any, Dict, Tuple

from hc_agent.core.http.preview import build_api_preview
from hc_agent.core.http.signature_summary import build_signature_summary


def execute(
    *,
    spec,
    mode: str,
    signer,
    timeout_s: int = 30,
) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """
    Execute or preview an HTTP request.
    """
    signed_headers, canonical_request, string_to_sign = signer.sign(spec)

    sig_summary = build_signature_summary(
        canonical_request=canonical_request,
        signed_headers=signed_headers,
        string_to_sign=string_to_sign,
    )

    if mode == "preview":
        return (
            {
                "api_preview": build_api_preview(spec),
                "signature_summary": sig_summary,
            },
            {
                "service": spec.service,
                "endpoint": spec.endpoint,
                "method": spec.method,
                "path": spec.path,
            },
        )

    url = spec.endpoint.rstrip("/") + spec.path
    start = time.time()

    import requests

    response = requests.request(
        method=spec.method,
        url=url,
        params=spec.query,
        headers={**(spec.headers or {}), **signed_headers},
        json=spec.json_body,
        timeout=timeout_s,
    )

    duration_ms = int((time.time() - start) * 1000)

    try:
        body = response.json()
    except Exception:
        body = {"raw": response.text}

    return (
        {
            "status_code": response.status_code,
            "response": body,
        },
        {
            "service": spec.service,
            "endpoint": spec.endpoint,
            "method": spec.method,
            "path": spec.path,
            "status": response.status_code,
            "request_id": response.headers.get("X-Request-Id", ""),
            "duration_ms": duration_ms,
            "signature_sha256": sig_summary.get("string_to_sign_sha256"),
        },
    )
