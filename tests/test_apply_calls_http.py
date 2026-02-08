import importlib
import inspect
import shutil
import tempfile

from autotest.client.shared.test_utils import mock, unittest


class MissingRequiredArguments(Exception):
    pass


class FakeResponse(object):
    def __init__(self, payload):
        self.status_code = 200
        self.headers = {"X-Request-Id": "test-request-id"}
        self._payload = payload

    def json(self):
        return self._payload


EVIDENCE_WHITELIST = set([
    "artifacts",
    "logs",
    "metadata",
    "metrics",
    "report",
])


def _import_optional(module_name):
    try:
        return importlib.import_module(module_name)
    except ImportError:
        return None


def _resolve_run_callable():
    candidates = [
        ("autotest.gateway", "hc_run"),
        ("autotest.gateway.hc", "hc_run"),
        ("autotest.gateway.runner", "run"),
        ("autotest.runner", "run"),
        ("autotest.hc", "hc_run"),
    ]
    for module_name, attr_name in candidates:
        module = _import_optional(module_name)
        if module is None:
            continue
        if hasattr(module, attr_name):
            return getattr(module, attr_name), "%s.%s" % (module_name, attr_name)
    return None, None


def _get_required_args(func):
    try:
        signature = inspect.signature(func)
    except (AttributeError, ValueError):
        argspec = inspect.getargspec(func)
        args = list(argspec.args or [])
        defaults = list(argspec.defaults or [])
        required = args[:len(args) - len(defaults)]
        return required, args
    required = []
    args = []
    for param in signature.parameters.values():
        if param.kind in (param.POSITIONAL_ONLY, param.POSITIONAL_OR_KEYWORD):
            args.append(param.name)
            if param.default is param.empty:
                required.append(param.name)
    return required, args


def _base_envelope(mode):
    return {
        "mode": mode,
        "inputs": {"test": True},
        "plan": [{"step": "noop"}],
    }


def _build_kwargs(func, mode, artifact_dir):
    required, args = _get_required_args(func)
    kwargs = {}
    for name in args:
        if name in ("self",):
            continue
        if name in ("mode", "run_mode", "operation"):
            kwargs[name] = mode
        elif name in ("preview", "dry_run"):
            kwargs[name] = mode == "preview"
        elif name == "apply":
            kwargs[name] = mode == "apply"
        elif name in (
            "artifacts_dir",
            "artifact_dir",
            "output_dir",
            "out_dir",
            "run_dir",
        ):
            kwargs[name] = artifact_dir
        elif name in ("envelope", "payload", "request", "run_request", "input", "data"):
            kwargs[name] = _base_envelope(mode)
    missing = [name for name in required if name not in kwargs and name != "self"]
    if missing:
        raise MissingRequiredArguments(
            "Missing required args: %s" % ", ".join(missing)
        )
    return kwargs


def _invoke_run(run_callable, mode, artifact_dir):
    kwargs = _build_kwargs(run_callable, mode, artifact_dir)
    return run_callable(**kwargs)


def _extract_evidence(result):
    if hasattr(result, "evidence"):
        return result.evidence
    if isinstance(result, dict):
        return result.get("evidence")
    return None


class ApplyCallsHTTPTest(unittest.TestCase):
    def test_apply_calls_http_once(self):
        requests_module = _import_optional("requests")
        if requests_module is None:
            self.skipTest("requests not installed")
        run_callable, _run_label = _resolve_run_callable()
        if run_callable is None:
            self.skipTest("No gateway or runner callable found")

        artifact_dir = tempfile.mkdtemp(prefix="autotest-apply-")
        payload = {"ok": True, "run_id": "run-123"}
        try:
            with mock.patch.object(
                requests_module,
                "request",
                return_value=FakeResponse(payload),
            ) as request_mock:
                try:
                    result = _invoke_run(run_callable, "apply", artifact_dir)
                except MissingRequiredArguments as exc:
                    self.skipTest(str(exc))

            self.assertEqual(request_mock.call_count, 1)

            if isinstance(result, dict):
                has_expected_fields = any(
                    key in result for key in ("run_id", "summary", "envelope")
                )
            else:
                has_expected_fields = any(
                    hasattr(result, key) for key in ("run_id", "summary", "envelope")
                )
            self.assertTrue(has_expected_fields)

            evidence = _extract_evidence(result)
            if isinstance(evidence, dict):
                extra_keys = set(evidence.keys()) - EVIDENCE_WHITELIST
                self.assertFalse(extra_keys)
        finally:
            shutil.rmtree(artifact_dir, ignore_errors=True)
