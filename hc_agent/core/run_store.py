"""Run storage utilities with atomic writes and index maintenance."""

from __future__ import annotations

import json
import os
import shutil
import uuid
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional


@dataclass
class RunIndexEntry:
    run_id: str
    tenant_id: Optional[str]
    created_at: str
    stage: Optional[str]
    ok: Optional[bool]


class RunStore:
    def __init__(self, root_dir: str | Path) -> None:
        self.root_dir = Path(root_dir)
        self.runs_dir = self.root_dir / "runs"
        self.index_path = self.runs_dir / "index.json"
        self.lock_path = self.runs_dir / ".index.lock"

    def write_json(
        self,
        run_id: str,
        relpath: str,
        payload: Any,
        *,
        tenant_id: Optional[str] = None,
        stage: Optional[str] = None,
        ok: Optional[bool] = None,
        created_at: Optional[str] = None,
    ) -> Path:
        target = self._run_path(run_id, relpath)
        serialized = json.dumps(payload, indent=2, sort_keys=True)
        self._write_text_atomic(target, serialized)
        self._update_index(
            run_id,
            tenant_id=tenant_id,
            stage=stage,
            ok=ok,
            created_at=created_at,
        )
        return target

    def write_text(
        self,
        run_id: str,
        relpath: str,
        content: str,
        *,
        tenant_id: Optional[str] = None,
        stage: Optional[str] = None,
        ok: Optional[bool] = None,
        created_at: Optional[str] = None,
    ) -> Path:
        target = self._run_path(run_id, relpath)
        self._write_text_atomic(target, content)
        self._update_index(
            run_id,
            tenant_id=tenant_id,
            stage=stage,
            ok=ok,
            created_at=created_at,
        )
        return target

    def read_json(self, run_id: str, relpath: str) -> Any:
        target = self._run_path(run_id, relpath)
        with target.open("r", encoding="utf-8") as handle:
            return json.load(handle)

    def read_text(self, run_id: str, relpath: str) -> str:
        target = self._run_path(run_id, relpath)
        return target.read_text(encoding="utf-8")

    def delete_run(self, run_id: str) -> None:
        run_dir = self.runs_dir / run_id
        with self._index_lock():
            if run_dir.exists():
                shutil.rmtree(run_dir)
            self._remove_from_index({run_id})

    def gc(self, max_age_seconds: float) -> List[str]:
        now = datetime.now(timezone.utc)
        threshold = now.timestamp() - max_age_seconds
        removed: List[str] = []
        with self._index_lock():
            entries = self._load_index_entries()
            for entry in entries:
                created_at = self._parse_time(entry.get("created_at"))
                if created_at is None:
                    continue
                if created_at.timestamp() < threshold:
                    run_id = entry.get("run_id")
                    if run_id:
                        run_dir = self.runs_dir / run_id
                        if run_dir.exists():
                            shutil.rmtree(run_dir)
                        removed.append(run_id)
            if removed:
                self._remove_from_index(set(removed))
        return removed

    def _run_path(self, run_id: str, relpath: str) -> Path:
        target = self.runs_dir / run_id / relpath
        target.parent.mkdir(parents=True, exist_ok=True)
        return target

    def _write_text_atomic(self, target: Path, content: str) -> None:
        data = content.encode("utf-8")
        self._write_bytes_atomic(target, data)

    def _write_bytes_atomic(self, target: Path, data: bytes) -> None:
        target.parent.mkdir(parents=True, exist_ok=True)
        temp_name = f".{target.name}.tmp.{uuid.uuid4().hex}"
        temp_path = target.with_name(temp_name)
        with temp_path.open("wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_path, target)

    def _update_index(
        self,
        run_id: str,
        *,
        tenant_id: Optional[str],
        stage: Optional[str],
        ok: Optional[bool],
        created_at: Optional[str],
    ) -> None:
        with self._index_lock():
            entries = self._load_index_entries()
            entry_map = {entry["run_id"]: entry for entry in entries if "run_id" in entry}
            entry = entry_map.get(run_id, {})
            entry["run_id"] = run_id
            if tenant_id is not None:
                entry["tenant_id"] = tenant_id
            if stage is not None:
                entry["stage"] = stage
            if ok is not None:
                entry["ok"] = ok
            if created_at is not None:
                entry["created_at"] = created_at
            else:
                entry.setdefault("created_at", self._now_iso())
            entry.setdefault("tenant_id", None)
            entry.setdefault("stage", None)
            entry.setdefault("ok", None)
            entry_map[run_id] = entry
            self._write_index_entries(entry_map.values())

    def _remove_from_index(self, run_ids: set[str]) -> None:
        entries = self._load_index_entries()
        remaining = [entry for entry in entries if entry.get("run_id") not in run_ids]
        self._write_index_entries(remaining)

    def _write_index_entries(self, entries: Iterable[Dict[str, Any]]) -> None:
        self.runs_dir.mkdir(parents=True, exist_ok=True)
        normalized = sorted(entries, key=lambda entry: entry.get("created_at", ""))
        data = json.dumps(normalized, indent=2, sort_keys=True)
        self._write_text_atomic(self.index_path, data)

    def _load_index_entries(self) -> List[Dict[str, Any]]:
        if not self.index_path.exists():
            return []
        try:
            with self.index_path.open("r", encoding="utf-8") as handle:
                data = json.load(handle)
        except json.JSONDecodeError:
            return []
        if isinstance(data, list):
            return [entry for entry in data if isinstance(entry, dict)]
        return []

    def _now_iso(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _parse_time(self, value: Optional[str]) -> Optional[datetime]:
        if not value:
            return None
        try:
            parsed = datetime.fromisoformat(value)
        except ValueError:
            return None
        if parsed.tzinfo is None:
            return parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(timezone.utc)

    @contextmanager
    def _index_lock(self) -> Iterable[None]:
        self.runs_dir.mkdir(parents=True, exist_ok=True)
        fd: Optional[int] = None
        try:
            fd = os.open(self.lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError:
            fd = None
        try:
            yield
        finally:
            if fd is not None:
                os.close(fd)
                try:
                    os.unlink(self.lock_path)
                except FileNotFoundError:
                    pass
