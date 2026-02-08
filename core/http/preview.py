"""Preview builder for HTTP requests."""

from __future__ import annotations

from typing import Any

from core.http.request_spec import RequestSpec
from core.http.signer import sign
from core.http.signature_summary import build_signature_summary


def build_preview(spec: RequestSpec) -> dict[str, Any]:
    """Build a preview payload without executing the HTTP request."""

    signed_headers, canonical_request, string_to_sign = sign(spec)
    signature_summary = build_signature_summary(
        signed_headers=signed_headers,
        canonical_request=canonical_request,
        string_to_sign=string_to_sign,
    )
    return {
        "request": {
            "method": spec.method.upper(),
            "url": spec.url,
            "headers": dict(spec.normalized_headers()),
            "params": dict(spec.params or {}),
            "body": spec.body,
            "timeout": spec.timeout,
        },
        "signature": signature_summary,
    }
