"""
Runtime context resolution.

This module builds the execution context used by handlers
and the unified runner.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Dict, Optional

from hc_agent.core.config.io import load_yaml_if_exists
from hc_agent.core.http.endpoints import EndpointContext


@dataclass
class RunContext:
    """
    Execution context shared across all handlers.
    """

    tenant_id: str
    region: str
    config_path: str
    endpoint_ctx: EndpointContext
    project_id: Optional[str] = None
    non_interactive: bool = True
    signer: Any = None


def _get_cfg_value(cfg: Dict[str, Any], path: str) -> Optional[str]:
    cur: Any = cfg
    for seg in path.split("."):
        if not isinstance(cur, dict):
            return None
        cur = cur.get(seg)
    return str(cur).strip() if cur else None


def resolve_project_id(*, config_path: str) -> Optional[str]:
    """
    Resolve Huawei Cloud project_id.

    Priority:
    1. Environment variable
    2. config.yaml
    """
    env_val = os.getenv("HC_PROJECT_ID") or os.getenv("HC_AGENT_PROJECT_ID")
    if env_val:
        return env_val.strip()

    cfg = load_yaml_if_exists(config_path)
    return _get_cfg_value(cfg, "context.project_id")
