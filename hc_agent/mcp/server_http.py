"""Optional FastAPI HTTP server."""

from __future__ import annotations

from importlib.util import find_spec


if find_spec("fastapi") and find_spec("pydantic"):
    from fastapi import FastAPI
    from pydantic import BaseModel

    app = FastAPI()

    class HealthResponse(BaseModel):
        status: str

    @app.get("/health", response_model=HealthResponse)
    def health() -> HealthResponse:
        return HealthResponse(status="ok")
else:
    app = None
