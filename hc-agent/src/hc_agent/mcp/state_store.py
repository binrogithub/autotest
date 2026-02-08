"""
Run state storage.
"""

from __future__ import annotations

import json
import shutil
import time
from pathlib import Path
from typing import Any, Dict


class RunStore:
    """
    File-based run storage with atomic writes.
    """

    def __init__(self, base_dir: str = "runs") -> None:
        self.base = Path(base_dir)
        self.base.mkdir(parents=True, exist_ok=True)

    def _run_dir(self, run_id: str) -> Path:
        return self.base / run_id

    def init_run(self, run_id: str) -> None:
        self._run_dir(run_id).mkdir(parents=True, exist_ok=True)

    def write_json(self, run_id: str, name: str, data: Dict[str, Any]) -> None:
        path = self._run_dir(run_id) / f"{name}.json"
        tmp = path.with_suffix(".tmp")
        with tmp.open("w", encoding="utf-8") as handle:
            json.dump(data, handle, indent=2)
        tmp.replace(path)

    def read_json(self, run_id: str, name: str) -> Dict[str, Any]:
        path = self._run_dir(run_id) / f"{name}.json"
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)

    def delete_run(self, run_id: str) -> None:
        shutil.rmtree(self._run_dir(run_id), ignore_errors=True)

    def gc(self, max_age_seconds: int) -> None:
        now = time.time()
        for run_dir in self.base.iterdir():
            if not run_dir.is_dir():
                continue
            if now - run_dir.stat().st_mtime > max_age_seconds:
                shutil.rmtree(run_dir, ignore_errors=True)
