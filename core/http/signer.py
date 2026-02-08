"""Deterministic request signer used for previews and apply mode."""

from __future__ import annotations

import hashlib
from urllib.parse import urlencode

from core.http.request_spec import RequestSpec


def _hash_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _canonical_headers(headers: dict[str, str]) -> tuple[str, str]:
    lowered = {key.lower(): " ".join(value.split()) for key, value in headers.items()}
    sorted_items = sorted(lowered.items())
    canonical = "".join(f"{key}:{value}\n" for key, value in sorted_items)
    signed_headers = ";".join(key for key, _ in sorted_items)
    return canonical, signed_headers


def sign(spec: RequestSpec) -> tuple[dict[str, str], str, str]:
    """Sign a request spec deterministically with no external dependencies."""

    method = spec.method.upper()
    headers = spec.normalized_headers()
    canonical_headers, signed_header_names = _canonical_headers(headers)
    canonical_query = urlencode(sorted((spec.params or {}).items()))
    body_hash = _hash_bytes(spec.body_bytes())
    canonical_request = "\n".join(
        [method, spec.url, canonical_query, canonical_headers, signed_header_names, body_hash]
    )
    string_to_sign = f"SIGNATURE\n{_hash_bytes(canonical_request.encode('utf-8'))}"
    signature_hash = _hash_bytes(string_to_sign.encode("utf-8"))
    signed_headers = dict(headers)
    signed_headers["x-signature"] = signature_hash
    return signed_headers, canonical_request, string_to_sign
