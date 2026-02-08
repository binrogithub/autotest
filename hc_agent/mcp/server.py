"""MCP server implementation for hc_agent."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Iterable, Mapping, MutableMapping, Optional
from urllib.parse import urlparse


ToolHandler = Callable[[Mapping[str, Any], Mapping[str, Any]], Any]


@dataclass
class McpServer:
    """MCP server with tool dispatch and run resource access."""

    run_store: Any
    tools: MutableMapping[str, ToolHandler] = field(default_factory=dict)
    admin_tools: MutableMapping[str, ToolHandler] = field(default_factory=dict)
    policy: Optional[Mapping[str, Any]] = None

    def __post_init__(self) -> None:
        if not self.tools:
            self.tools.update(
                {
                    "hc_tools_search": self._missing_tool_stub("hc_tools_search"),
                    "hc_run": self._missing_tool_stub("hc_run"),
                    "hc_run_demo": self._missing_tool_stub("hc_run_demo"),
                    "hc_doctor_fix": self._missing_tool_stub("hc_doctor_fix"),
                }
            )

    @staticmethod
    def _missing_tool_stub(name: str) -> ToolHandler:
        def _stub(_params: Mapping[str, Any], _ctx: Mapping[str, Any]) -> Dict[str, Any]:
            return {
                "ok": False,
                "error": {
                    "code": "tool_not_configured",
                    "message": f"Tool '{name}' is not configured.",
                    "tool": name,
                },
            }

        return _stub

    def list_tools(self) -> Dict[str, Any]:
        """List available tool names."""

        tool_names = sorted(set(self.tools) | set(self.admin_tools))
        return {"ok": True, "tools": tool_names}

    def call_tool(
        self, name: str, params: Optional[Mapping[str, Any]], ctx: Optional[Mapping[str, Any]]
    ) -> Any:
        """Dispatch to a tool by name."""

        params = params or {}
        ctx = ctx or {}

        if name in self.admin_tools:
            if not self._policy_allows_admin(ctx):
                return {
                    "ok": False,
                    "error": {
                        "code": "forbidden",
                        "message": f"Tool '{name}' requires admin policy approval.",
                        "tool": name,
                    },
                }
            return self.admin_tools[name](params, ctx)

        if name in self.tools:
            return self.tools[name](params, ctx)

        return {
            "ok": False,
            "error": {
                "code": "unknown_tool",
                "message": f"Tool '{name}' is not registered.",
                "tool": name,
            },
        }

    def read_resource(self, uri: str) -> Dict[str, Any]:
        """Read a resource from the run store."""

        parsed = urlparse(uri)
        if parsed.scheme != "hc-run":
            return {
                "ok": False,
                "error": {
                    "code": "unsupported_scheme",
                    "message": f"Unsupported URI scheme '{parsed.scheme}'.",
                    "uri": uri,
                },
            }

        run_id, artifact_path = self._parse_run_uri(parsed)
        if not run_id:
            return {
                "ok": False,
                "error": {
                    "code": "invalid_uri",
                    "message": "Missing run id in hc-run URI.",
                    "uri": uri,
                },
            }

        if artifact_path:
            artifact = self._read_artifact(run_id, artifact_path)
            return {"ok": True, "uri": uri, "content": artifact}

        run_info = self._read_run_info(run_id)
        return {"ok": True, "uri": uri, "content": run_info}

    def list_resources(self, prefix: Optional[str] = None) -> Dict[str, Any]:
        """Optionally list resources from the run store."""

        if prefix is None:
            return {"ok": True, "resources": []}

        parsed = urlparse(prefix)
        if parsed.scheme != "hc-run":
            return {"ok": False, "error": {"code": "unsupported_scheme", "uri": prefix}}

        run_id, artifact_prefix = self._parse_run_uri(parsed)
        if not run_id:
            return {"ok": False, "error": {"code": "invalid_uri", "uri": prefix}}

        list_method = getattr(self.run_store, "list_artifacts", None)
        if callable(list_method):
            artifacts = list_method(run_id, artifact_prefix or None)
        else:
            artifacts = []

        resources = [self._format_run_resource(run_id, artifact) for artifact in artifacts]
        return {"ok": True, "resources": resources}

    def _policy_allows_admin(self, ctx: Mapping[str, Any]) -> bool:
        policy = ctx.get("policy") if isinstance(ctx, Mapping) else None
        if isinstance(policy, Mapping) and policy.get("allow_admin_tools") is True:
            return True
        if isinstance(ctx, Mapping) and ctx.get("allow_admin_tools") is True:
            return True
        if isinstance(self.policy, Mapping) and self.policy.get("allow_admin_tools") is True:
            return True
        return False

    @staticmethod
    def _parse_run_uri(parsed_uri) -> tuple[str, str]:
        run_id = parsed_uri.netloc
        artifact_path = parsed_uri.path.lstrip("/")
        if not run_id and parsed_uri.path:
            parts = parsed_uri.path.lstrip("/").split("/", 1)
            run_id = parts[0]
            artifact_path = parts[1] if len(parts) > 1 else ""
        return run_id, artifact_path

    def _read_artifact(self, run_id: str, artifact_path: str) -> Any:
        for method_name in ("read_artifact", "get_artifact", "open_artifact"):
            method = getattr(self.run_store, method_name, None)
            if callable(method):
                result = method(run_id, artifact_path)
                if method_name == "open_artifact" and hasattr(result, "read"):
                    return result.read()
                return result
        raise AttributeError("RunStore does not support artifact retrieval")

    def _read_run_info(self, run_id: str) -> Any:
        for method_name in ("get_run", "read_run", "run_info"):
            method = getattr(self.run_store, method_name, None)
            if callable(method):
                return method(run_id)
        return {"run_id": run_id}

    @staticmethod
    def _format_run_resource(run_id: str, artifact: Any) -> Dict[str, Any]:
        if isinstance(artifact, Mapping):
            path = artifact.get("path") or artifact.get("name") or ""
            metadata = dict(artifact)
        else:
            path = str(artifact)
            metadata = {"path": path}
        uri = f"hc-run://{run_id}/{path}" if path else f"hc-run://{run_id}"
        metadata.setdefault("uri", uri)
        return metadata
