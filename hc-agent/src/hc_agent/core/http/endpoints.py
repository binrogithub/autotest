"""
Endpoint resolution utilities.

This module builds service endpoints using table-driven templates
for both public Huawei Cloud and HCSO environments.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class EndpointContext:
    base_domain: str = "myhuaweicloud.com"
    hcso_base_domain: Optional[str] = None
    use_hcso: bool = False
    endpoint_template_public: str = "{service}.{region}.{base}"
    endpoint_template_hcso: str = "{service}.{region}.{base}"


SERVICE_TEMPLATES_PUBLIC: Dict[str, str] = {
    "*": "{service}.{region}.{base}",
    "iam": "iam.{region}.{base}",
    "ecs": "ecs.{region}.{base}",
    "vpc": "vpc.{region}.{base}",
    "evs": "evs.{region}.{base}",
    "rds": "rds.{region}.{base}",
    "obs": "obs.{region}.{base}",
}


SERVICE_TEMPLATES_HCSO: Dict[str, str] = {
    "*": "{service}.{region}.{base}",
    "ecs": "ecs.{region}.{base}",
    "vpc": "vpc.{region}.{base}",
    "rds": "rds.{region}.{base}",
    "obs": "obs.{region}.{base}",
}


def build_endpoint(*, service: str, region: str, ctx: EndpointContext) -> str:
    """
    Build a service endpoint host.

    Returns host only (no scheme).
    """
    base = ctx.hcso_base_domain if ctx.use_hcso else ctx.base_domain
    if not base:
        raise ValueError("Base domain is not configured")

    templates = SERVICE_TEMPLATES_HCSO if ctx.use_hcso else SERVICE_TEMPLATES_PUBLIC
    template = templates.get(service) or templates.get("*")

    return template.format(
        service=service,
        region=region,
        base=base,
    )
