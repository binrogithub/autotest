"""Gateway for running preview/apply flows.

Example:
    store = RunStore("./runs")
    def preview(payload):
        return {"status": "ok", "payload": payload}
    def apply(payload):
        return {"status": "applied", "payload": payload}
    record = hc_run(preview, apply, store, payload={"target": "demo"})
"""

import argparse
import uuid
from datetime import datetime, timezone

from . import evidence, run_summary, sanitize
from .state_store import RunStore


def hc_run(preview_fn, apply_fn, run_store, payload=None):
    """Run preview/apply, sanitize outputs, and persist results."""
    run_id = uuid.uuid4().hex
    payload = payload or {}

    preview_result = preview_fn(payload)
    apply_result = apply_fn(payload)

    sanitized_preview = sanitize.sanitize_value(preview_result)
    sanitized_apply = sanitize.sanitize_value(apply_result)

    run_record = {
        "run_id": run_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "payload": sanitize.sanitize_value(payload),
        "preview": sanitized_preview,
        "apply": sanitized_apply,
        "evidence": evidence.build_evidence(sanitized_preview, sanitized_apply),
    }

    run_store.write_run(run_id, run_record)
    return run_record


def _demo_preview(payload):
    return {"status": "previewed", "payload": payload}


def _demo_apply(payload):
    return {"status": "applied", "payload": payload}


def main(argv=None):
    parser = argparse.ArgumentParser(description="Run an MCP health check demo")
    parser.add_argument("--store-dir", default="./mcp_runs")
    parser.add_argument("--report", default="report.md")
    args = parser.parse_args(argv)

    store = RunStore(args.store_dir)
    run_record = hc_run(_demo_preview, _demo_apply, store, payload={"demo": True})
    run_summary.write_report(args.report, run_record)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
