"""Request specification used for preview and apply execution."""

from __future__ import annotations

from dataclasses import dataclass, field
import json
from typing import Any, Mapping, MutableMapping, Optional


@dataclass(frozen=True)
class RequestSpec:
    """Defines a deterministic request shape for preview/apply flows."""

    method: str
    url: str
    headers: Mapping[str, str] = field(default_factory=dict)
    params: Mapping[str, str] = field(default_factory=dict)
    body: Optional[Any] = None
    timeout: Optional[float] = None

    def normalized_headers(self) -> dict[str, str]:
        return {
            str(key).strip(): str(value).strip()
            for key, value in (self.headers or {}).items()
        }

    def body_bytes(self) -> bytes:
        if self.body is None:
            return b""
        if isinstance(self.body, bytes):
            return self.body
        if isinstance(self.body, str):
            return self.body.encode("utf-8")
        return json.dumps(self.body, sort_keys=True, separators=(",", ":")).encode(
            "utf-8"
        )

    def to_requests_kwargs(self) -> MutableMapping[str, Any]:
        kwargs: MutableMapping[str, Any] = {
            "headers": self.normalized_headers(),
            "params": dict(self.params or {}),
        }
        if self.timeout is not None:
            kwargs["timeout"] = self.timeout
        if self.body is not None:
            if isinstance(self.body, (bytes, str)):
                kwargs["data"] = self.body
            else:
                kwargs["json"] = self.body
        return kwargs
