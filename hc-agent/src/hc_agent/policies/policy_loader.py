"""
Policy loader for hc-agent.

Loads YAML policy files and returns tenant-specific policy settings.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass
class TenantPolicy:
    tenant_id: str
    risk_max: str = "medium"        # low | medium | high
    allow_write: bool = False
    expose_legacy_tools: bool = False
    allowed_tools: List[str] = None

    def __post_init__(self) -> None:
        if self.allowed_tools is None:
            self.allowed_tools = []


def load_policy_file(path: str) -> Dict[str, Any]:
    """
    Load a policy YAML file into a dictionary.
    """
    if not path or not os.path.exists(path):
        return {}

    try:
        import yaml

        with open(path, "r", encoding="utf-8") as handle:
            data = yaml.safe_load(handle)
            return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def get_tenant_policy(policy_data: Dict[str, Any], tenant_id: str) -> TenantPolicy:
    """
    Return the policy for a given tenant_id.

    Merges tenant policy on top of defaults.
    """
    tenant_id = (tenant_id or "default").strip()

    defaults = policy_data.get("defaults") if isinstance(policy_data.get("defaults"), dict) else {}
    tenants = policy_data.get("tenants") if isinstance(policy_data.get("tenants"), dict) else {}
    tcfg = tenants.get(tenant_id) if isinstance(tenants.get(tenant_id), dict) else {}

    risk_max = str(tcfg.get("risk_max") or defaults.get("risk_max") or "medium").strip().lower()
    allow_write = bool(tcfg.get("allow_write") if "allow_write" in tcfg else defaults.get("allow_write", False))
    expose_legacy = bool(
        tcfg.get("expose_legacy_tools") if "expose_legacy_tools" in tcfg else defaults.get("expose_legacy_tools", False)
    )

    allowed_tools = tcfg.get("allowed_tools") if "allowed_tools" in tcfg else defaults.get("allowed_tools", [])
    if not isinstance(allowed_tools, list):
        allowed_tools = []

    return TenantPolicy(
        tenant_id=tenant_id,
        risk_max=risk_max,
        allow_write=allow_write,
        expose_legacy_tools=expose_legacy,
        allowed_tools=[str(x) for x in allowed_tools],
    )


def load_tenant_policy(path: str, tenant_id: str) -> TenantPolicy:
    """
    Convenience helper: load file + return tenant policy.
    """
    data = load_policy_file(path)
    return get_tenant_policy(data, tenant_id)
