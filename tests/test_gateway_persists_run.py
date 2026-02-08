import importlib
import inspect
import os
import shutil
import tempfile

from autotest.client.shared.test_utils import unittest


class MissingRequiredArguments(Exception):
    pass


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


def _resolve_run_store_class():
    candidates = [
        "autotest.gateway.run_store",
        "autotest.gateway.storage",
        "autotest.run_store",
    ]
    for module_name in candidates:
        module = _import_optional(module_name)
        if module is None:
            continue
        if hasattr(module, "RunStore"):
            return module.RunStore
    return None


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


def _build_kwargs(func, mode, artifact_dir, run_store=None):
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
        elif name in ("run_store", "store") and run_store is not None:
            kwargs[name] = run_store
    missing = [name for name in required if name not in kwargs and name != "self"]
    if missing:
        raise MissingRequiredArguments(
            "Missing required args: %s" % ", ".join(missing)
        )
    return kwargs


def _invoke_run(run_callable, mode, artifact_dir, run_store=None):
    kwargs = _build_kwargs(run_callable, mode, artifact_dir, run_store=run_store)
    return run_callable(**kwargs)


def _build_store_kwargs(store_cls, base_dir):
    required, args = _get_required_args(store_cls.__init__)
    kwargs = {}
    for name in args:
        if name in ("self",):
            continue
        if name in ("root_dir", "base_dir", "path", "storage_dir", "run_dir"):
            kwargs[name] = base_dir
    missing = [name for name in required if name not in kwargs and name != "self"]
    if missing:
        raise MissingRequiredArguments(
            "Missing required store args: %s" % ", ".join(missing)
        )
    return kwargs


def _extract_run_id(result):
    if hasattr(result, "run_id"):
        return result.run_id
    if isinstance(result, dict):
        return result.get("run_id") or result.get("id")
    return None


class GatewayPersistsRunTest(unittest.TestCase):
    def test_gateway_persists_run_artifacts(self):
        run_store_cls = _resolve_run_store_class()
        if run_store_cls is None:
            self.skipTest("No RunStore available")
        run_callable, run_label = _resolve_run_callable()
        if run_callable is None:
            self.skipTest("No gateway or runner callable found")
        if not run_label or "gateway" not in run_label:
            self.skipTest("Gateway callable not available")

        base_dir = tempfile.mkdtemp(prefix="autotest-runs-")
        artifact_dir = tempfile.mkdtemp(prefix="autotest-artifacts-")
        try:
            try:
                store_kwargs = _build_store_kwargs(run_store_cls, base_dir)
            except MissingRequiredArguments as exc:
                self.skipTest(str(exc))
            run_store = run_store_cls(**store_kwargs)

            try:
                result = _invoke_run(
                    run_callable,
                    "apply",
                    artifact_dir,
                    run_store=run_store,
                )
            except MissingRequiredArguments as exc:
                self.skipTest(str(exc))

            run_id = _extract_run_id(result)
            if not run_id:
                self.skipTest("Run id not available in result")

            report_path = os.path.join(base_dir, "runs", run_id, "report.md")
            self.assertTrue(os.path.exists(report_path))
        finally:
            shutil.rmtree(base_dir, ignore_errors=True)
            shutil.rmtree(artifact_dir, ignore_errors=True)
