"""FastAPI application skeleton (WBS-14.2).

Feature modules add their routers here in their own pull requests.
"""

from fastapi import FastAPI


def create_app() -> FastAPI:
    app = FastAPI(title="SynapseITU API", version="0.1.0")

    @app.get("/health", tags=["ops"])
    async def health() -> dict[str, str]:
        """Liveness endpoint for container health checks and the uptime monitor (MC-14)."""
        return {"status": "ok", "service": "backend"}

    return app


app = create_app()
