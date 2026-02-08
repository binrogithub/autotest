"""Execute HTTP requests in preview or apply modes."""

from __future__ import annotations

from typing import Any, Mapping, Tuple

import requests

from core.http.preview import build_preview
from core.http.request_spec import RequestSpec
from core.http.signer import sign
from core.http.signature_summary import build_signature_summary


RequestResult = Tuple[dict[str, Any], dict[str, Any]]


def _extract_request_id(headers: Mapping[str, str]) -> str | None:
    for key in ("x-request-id", "request-id", "x-amzn-requestid", "x-amz-request-id"):
        if key in headers:
            return headers[key]
    return None


def execute(spec: RequestSpec, mode: str = "preview") -> RequestResult:
    """Execute a request in preview or apply mode.

    Returns a tuple of (result_dict, raw_evidence_dict).
    """

    if mode == "preview":
        preview_data = build_preview(spec)
        signature_summary = preview_data["signature"]
        result = {
            "mode": "preview",
            "preview": preview_data,
            "signature_hash": signature_summary.get("signature_hash"),
        }
        return result, {"preview": preview_data}

    signed_headers, canonical_request, string_to_sign = sign(spec)
    signature_summary = build_signature_summary(
        signed_headers=signed_headers,
        canonical_request=canonical_request,
        string_to_sign=string_to_sign,
    )

    request_kwargs = spec.to_requests_kwargs()
    request_kwargs["headers"] = signed_headers
    response = requests.request(spec.method, spec.url, **request_kwargs)
    response_headers = dict(getattr(response, "headers", {}) or {})
    request_id = _extract_request_id(
        {key.lower(): value for key, value in response_headers.items()}
    )
    result = {
        "mode": "apply",
        "status_code": getattr(response, "status_code", None),
        "request_id": request_id,
        "signature_hash": signature_summary.get("signature_hash"),
    }
    raw_evidence = {
        "response": {
            "status_code": getattr(response, "status_code", None),
            "headers": response_headers,
            "body": getattr(response, "text", None),
        },
        "signature": signature_summary,
    }
    return result, raw_evidence
