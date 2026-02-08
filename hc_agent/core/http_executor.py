"""HTTP executor that resolves service endpoints."""

from __future__ import annotations

from typing import Mapping, Optional

from hc_agent.core import endpoints


class HttpExecutor:
    """Resolves service endpoints for HTTP requests."""

    def __init__(
        self,
        config: Optional[Mapping[str, object]] = None,
        environ: Optional[Mapping[str, str]] = None,
        context: Optional[endpoints.EndpointContext] = None,
    ) -> None:
        self._context = context or endpoints.build_context(config=config, environ=environ)

    def resolve_service_url(
        self,
        service: str,
        region: Optional[str] = None,
        base: Optional[str] = None,
        scheme: str = "https",
    ) -> str:
        host = endpoints.resolve_endpoint(service, self._context, region=region, base=base)
        return f"{scheme}://{host}"
