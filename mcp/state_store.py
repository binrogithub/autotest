"""Persistent run storage for MCP runs.

Example:
    store = RunStore("./runs")
    store.write_run("abc123", {"run_id": "abc123"})
    loaded = store.read_run("abc123")
"""

import json
import os
import tempfile


class RunStore:
    """Store run records on disk with atomic writes."""

    def __init__(self, root_dir):
        self.root_dir = root_dir
        os.makedirs(self.root_dir, exist_ok=True)

    def _run_path(self, run_id):
        return os.path.join(self.root_dir, f"{run_id}.json")

    def write_run(self, run_id, run_record):
        """Atomically write a run record to disk."""
        path = self._run_path(run_id)
        directory = os.path.dirname(path)
        os.makedirs(directory, exist_ok=True)
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            delete=False,
            dir=directory,
            prefix=f".{run_id}.",
            suffix=".tmp",
        ) as handle:
            json.dump(run_record, handle, indent=2, sort_keys=True, ensure_ascii=False)
            handle.write("\n")
            temp_name = handle.name
        os.replace(temp_name, path)

    def read_run(self, run_id):
        """Read a run record from disk."""
        path = self._run_path(run_id)
        with open(path, encoding="utf-8") as handle:
            return json.load(handle)

    def list_runs(self):
        """Return known run ids sorted for deterministic output."""
        runs = []
        for name in os.listdir(self.root_dir):
            if name.endswith(".json"):
                runs.append(name[: -len(".json")])
        return sorted(runs)
