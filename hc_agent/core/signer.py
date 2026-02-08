"""Request signer that uses endpoint context for service resolution."""

from __future__ import annotations

from typing import Mapping, Optional

from hc_agent.core import endpoints


class RequestSigner:
    """Minimal signer stub that resolves service endpoints."""

    def __init__(
        self,
        config: Optional[Mapping[str, object]] = None,
        environ: Optional[Mapping[str, str]] = None,
        context: Optional[endpoints.EndpointContext] = None,
    ) -> None:
        self._context = context or endpoints.build_context(config=config, environ=environ)

    def resolve_service_endpoint(
        self,
        service: str,
        region: Optional[str] = None,
        base: Optional[str] = None,
    ) -> str:
        return endpoints.resolve_endpoint(service, self._context, region=region, base=base)
