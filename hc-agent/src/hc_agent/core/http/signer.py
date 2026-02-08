"""
Huawei Cloud request signer (HWC-HMAC-SHA256).

This is a placeholder interface. The actual implementation
should generate signed headers and signing material.
"""

from __future__ import annotations

from typing import Dict, Tuple


class HwSigner:
    """
    Huawei Cloud HWC-HMAC-SHA256 signer interface.
    """

    def sign(self, spec) -> Tuple[Dict[str, str], str, str]:
        """
        Sign a request.

        Returns:
        - signed_headers
        - canonical_request
        - string_to_sign
        """
        raise NotImplementedError("Signer implementation is required")
