from unittest import mock

import hc_agent


class FakeResponse:
    def __init__(self, status_code=200, json_data=None):
        self.status_code = status_code
        self._json_data = json_data or {}

    def json(self):
        return self._json_data


def test_preview_does_not_call_requests(monkeypatch):
    def raise_if_called(*args, **kwargs):
        raise AssertionError("should not call")

    monkeypatch.setattr(hc_agent.requests, "request", raise_if_called)
    result = hc_agent.preview({"run": "preview"})
    assert result["mode"] == "preview"


def test_apply_calls_requests_once(monkeypatch):
    fake_response = FakeResponse(status_code=202)
    request_mock = mock.Mock(return_value=fake_response)
    monkeypatch.setattr(hc_agent.requests, "request", request_mock)

    response = hc_agent.apply({"run": "apply"})

    assert response is fake_response
    request_mock.assert_called_once()


def test_gateway_writes_run_artifacts(tmp_path):
    run_id = hc_agent.gateway_run({"run": "gateway"}, runstore_root=tmp_path)
    report_path = tmp_path / "runs" / run_id / "report.md"
    assert report_path.exists()
