import io
import os
import uuid

import requests


def preview(payload):
    return {"mode": "preview", "payload": payload}


def apply(payload, request_fn=None):
    if request_fn is None:
        request_fn = requests.request
    return request_fn("POST", "http://hc-agent/apply", json=payload)


class RunStore:
    def __init__(self, root):
        self.root = root

    def run_dir(self, run_id):
        return os.path.join(self.root, "runs", run_id)

    def write_report(self, run_id, content):
        run_dir = self.run_dir(run_id)
        os.makedirs(run_dir, exist_ok=True)
        report_path = os.path.join(run_dir, "report.md")
        with io.open(report_path, "w", encoding="utf-8") as handle:
            handle.write(content)
        return report_path


def gateway_run(payload, runstore_root, run_id=None, report_contents=None):
    del payload
    run_id = run_id or str(uuid.uuid4())
    report_contents = report_contents or "hc-agent report"
    runstore = RunStore(runstore_root)
    runstore.write_report(run_id, report_contents)
    return run_id
