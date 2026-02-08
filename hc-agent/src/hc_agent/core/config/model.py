"""
Configuration data models.

This module defines minimal dataclasses used to represent
hc-agent configuration structures in memory.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class EndpointConfig:
    use_hcso: bool = False
    base_domain: str = "myhuaweicloud.com"
    hcso_base_domain: Optional[str] = None
    endpoint_template_public: str = "{service}.{region}.{base}"
    endpoint_template_hcso: str = "{service}.{region}.{base}"


@dataclass
class NetworkDefaults:
    vpc_id: Optional[str] = None
    subnet_id: Optional[str] = None
    security_group_id: Optional[str] = None
    prefer_tags: Dict[str, str] | None = None
    prefer_name_keywords: list[str] | None = None


@dataclass
class RuntimeConfig:
    region: str
    project_id: Optional[str] = None
    non_interactive: bool = True
