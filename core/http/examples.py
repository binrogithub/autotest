"""Examples demonstrating preview and apply execution."""

from __future__ import annotations

from unittest import mock

from core.http.executor import execute
from core.http.request_spec import RequestSpec


def preview_example() -> tuple[dict, dict]:
    spec = RequestSpec(
        method="POST",
        url="https://api.example.test/v1/widgets",
        headers={"Content-Type": "application/json"},
        body={"name": "preview"},
    )
    return execute(spec, mode="preview")


def apply_example() -> tuple[dict, dict]:
    spec = RequestSpec(
        method="GET",
        url="https://api.example.test/v1/widgets",
        headers={"Accept": "application/json"},
    )

    mock_response = mock.Mock()
    mock_response.status_code = 200
    mock_response.headers = {"X-Request-Id": "req-123"}
    mock_response.text = "ok"

    with mock.patch("requests.request", return_value=mock_response):
        return execute(spec, mode="apply")
