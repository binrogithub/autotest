"""Endpoint resolution for hc_agent."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Iterable, Mapping, MutableMapping, Optional


DEFAULT_TEMPLATES = ("{service}.{region}.{base}", "{service}.{base}")

SERVICE_TEMPLATES = {
    "rds": ("rds.{region}.{base}", "rds.{base}"),
    "aom": ("aom.{region}.{base}", "aom.{base}"),
}


@dataclass(frozen=True)
class EndpointContext:
    """Resolved endpoint context."""

    region: Optional[str] = None
    base: Optional[str] = None
    overrides: Mapping[str, str] = field(default_factory=dict)


def _get_config_value(config: Mapping[str, object], *keys: str) -> Optional[str]:
    value = config
    for key in keys:
        if not isinstance(value, Mapping) or key not in value:
            return None
        value = value[key]
    if value is None:
        return None
    return str(value)


def _load_overrides(config: Mapping[str, object]) -> MutableMapping[str, str]:
    overrides: MutableMapping[str, str] = {}
    for key in ("endpoints", "endpoint_overrides"):
        mapping = config.get(key)
        if isinstance(mapping, Mapping):
            for service, endpoint in mapping.items():
                overrides[str(service).lower()] = str(endpoint)
    agent_mapping = config.get("agent")
    if isinstance(agent_mapping, Mapping):
        mapping = agent_mapping.get("endpoints")
        if isinstance(mapping, Mapping):
            for service, endpoint in mapping.items():
                overrides[str(service).lower()] = str(endpoint)
    return overrides


def _merge_env_overrides(overrides: MutableMapping[str, str], environ: Mapping[str, str]) -> None:
    for key, value in environ.items():
        if not key.startswith("HC_ENDPOINT_"):
            continue
        service = key[len("HC_ENDPOINT_") :].strip().lower()
        if not service:
            continue
        overrides[service] = value


def build_context(
    config: Optional[Mapping[str, object]] = None,
    environ: Optional[Mapping[str, str]] = None,
) -> EndpointContext:
    """Create an endpoint context from config and environment variables."""

    config = config or {}
    environ = environ or os.environ

    region = (
        environ.get("HC_AGENT_REGION")
        or _get_config_value(config, "agent", "region")
        or _get_config_value(config, "region")
    )
    base = (
        environ.get("HC_AGENT_BASE")
        or environ.get("HC_AGENT_BASE_DOMAIN")
        or _get_config_value(config, "agent", "base")
        or _get_config_value(config, "base")
    )

    overrides = _load_overrides(config)
    _merge_env_overrides(overrides, environ)

    return EndpointContext(region=region, base=base, overrides=overrides)


def _iter_templates(service: str) -> Iterable[str]:
    service = service.lower()
    return SERVICE_TEMPLATES.get(service, DEFAULT_TEMPLATES)


def resolve_endpoint(
    service: str,
    context: EndpointContext,
    region: Optional[str] = None,
    base: Optional[str] = None,
) -> str:
    """Resolve the endpoint for a service using overrides and templates."""

    if not service:
        raise ValueError("service name is required")

    service_key = service.lower()
    if service_key in context.overrides:
        return context.overrides[service_key]

    region = region or context.region
    base = base or context.base

    if not base:
        raise ValueError("base domain is required to resolve endpoint")

    for template in _iter_templates(service_key):
        if "{region}" in template and not region:
            continue
        return template.format(service=service_key, region=region, base=base)

    raise ValueError(f"unable to resolve endpoint for {service_key}")
