"""Resource handler for hc-run artifacts."""

from __future__ import annotations

import json
import posixpath
import re
from dataclasses import dataclass
from typing import Any, Mapping
from urllib.parse import urlparse


class InvalidResourceUri(ValueError):
    """Raised when a hc-run URI is invalid."""


class ResourceNotFound(FileNotFoundError):
    """Raised when an artifact cannot be found."""


class UnsupportedArtifactType(ValueError):
    """Raised when an artifact type is unsupported."""


_SAFE_PATH_RE = re.compile(r"^[A-Za-z0-9._\-/]+$")


@dataclass(frozen=True)
class ResourceResponse:
    content_type: str
    body: str


@dataclass(frozen=True)
class ParsedResource:
    run_id: str
    artifact_path: str


class RunStore:
    """Minimal RunStore protocol for resource handlers."""

    def read_artifact(self, run_id: str, artifact_path: str) -> bytes | str:
        raise NotImplementedError


class HcRunResourceHandler:
    """Read-only handler for hc-run artifacts."""

    def __init__(self, run_store: RunStore) -> None:
        self._run_store = run_store

    def get(self, uri: str) -> ResourceResponse:
        parsed = parse_hc_run_uri(uri)
        artifact = self._read_artifact(parsed)
        return _build_response(parsed.artifact_path, artifact)

    def _read_artifact(self, parsed: ParsedResource) -> bytes | str:
        try:
            return self._run_store.read_artifact(parsed.run_id, parsed.artifact_path)
        except FileNotFoundError as exc:
            raise ResourceNotFound(
                f"Artifact not found for run {parsed.run_id}: {parsed.artifact_path}"
            ) from exc


def parse_hc_run_uri(uri: str) -> ParsedResource:
    parsed = urlparse(uri)
    if parsed.scheme != "hc-run":
        raise InvalidResourceUri("URI must start with hc-run://")
    if not parsed.netloc:
        raise InvalidResourceUri("Run ID is required in hc-run URI")
    if parsed.params or parsed.query or parsed.fragment:
        raise InvalidResourceUri("hc-run URI cannot include params, query, or fragment")

    artifact_path = parsed.path.lstrip("/")
    if not artifact_path:
        raise InvalidResourceUri("Artifact path is required in hc-run URI")

    normalized = posixpath.normpath(artifact_path)
    if normalized.startswith("../") or normalized == "..":
        raise InvalidResourceUri("Artifact path cannot escape the run root")

    if normalized != artifact_path:
        raise InvalidResourceUri("Artifact path must be normalized")

    if "\\" in artifact_path or "\x00" in artifact_path:
        raise InvalidResourceUri("Artifact path contains invalid characters")

    if not _SAFE_PATH_RE.match(artifact_path):
        raise InvalidResourceUri("Artifact path contains unsafe characters")

    return ParsedResource(run_id=parsed.netloc, artifact_path=artifact_path)


def _build_response(artifact_path: str, data: bytes | str) -> ResourceResponse:
    if isinstance(data, bytes):
        text = data.decode("utf-8", errors="replace")
    else:
        text = data

    text = text.replace("\x00", "")

    if artifact_path.endswith((".md", ".markdown")):
        return ResourceResponse(content_type="text/markdown; charset=utf-8", body=text)

    if artifact_path.endswith(".json"):
        return _json_response(text)

    raise UnsupportedArtifactType("Only markdown and JSON artifacts are supported")


def _json_response(text: str) -> ResourceResponse:
    try:
        payload: Any = json.loads(text)
    except json.JSONDecodeError as exc:
        raise UnsupportedArtifactType("Artifact is not valid JSON") from exc

    sanitized = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    return ResourceResponse(content_type="application/json", body=sanitized)


def handle_hc_run_resource(run_store: RunStore, uri: str) -> Mapping[str, str]:
    """Convenience wrapper for resource handler integration."""
    handler = HcRunResourceHandler(run_store)
    response = handler.get(uri)
    return {"content_type": response.content_type, "body": response.body}
