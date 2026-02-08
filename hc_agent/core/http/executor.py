"""HTTP executor."""

from __future__ import annotations

from typing import Any


def execute(method: str, url: str, **kwargs: Any) -> Any:
    """Execute an HTTP request."""
    if url.startswith("http"):
        import requests

        return requests.request(method, url, **kwargs)

    raise ValueError(f"Unsupported URL: {url}")
