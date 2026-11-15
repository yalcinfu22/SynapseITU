"""Independent FastAPI application for WBS-13.1.

Run alongside the main SynapseITU API as a separate process/container:
    uvicorn app.dummy_university.main:app --host 0.0.0.0 --port 8001
"""

from collections.abc import Mapping
from typing import Any

from fastapi import FastAPI, HTTPException, Request

from app.dummy_university.models import Lab, Position, Program
from app.dummy_university.seed import LABS, POSITIONS, PROGRAMS


def _as_response(request: Request, record: Mapping[str, Any], route_name: str) -> dict[str, Any]:
    """Add a source URL that the later data agent can fetch and retain."""
    return {**record, "source_url": str(request.url_for(route_name, record_id=record["id"]))}


def _find_record(records: tuple[dict[str, Any], ...], record_id: str) -> dict[str, Any]:
    record = next((item for item in records if item["id"] == record_id), None)
    if record is None:
        raise HTTPException(status_code=404, detail="Record not found")
    return record


def create_app() -> FastAPI:
    """Create the dummy university service independently of SynapseITU's main app."""
    app = FastAPI(title="SynapseITU Dummy University API", version="0.1.0")

    @app.get("/health", tags=["ops"])
    async def health() -> dict[str, str]:
        return {"status": "ok", "service": "dummy-university"}

    @app.get("/programs", response_model=list[Program], tags=["university"])
    async def list_programs(request: Request) -> list[dict[str, Any]]:
        return [_as_response(request, item, "get_program") for item in PROGRAMS]

    @app.get("/programs/{record_id}", response_model=Program, tags=["university"])
    async def get_program(record_id: str, request: Request) -> dict[str, Any]:
        return _as_response(request, _find_record(PROGRAMS, record_id), "get_program")

    @app.get("/labs", response_model=list[Lab], tags=["university"])
    async def list_labs(request: Request) -> list[dict[str, Any]]:
        return [_as_response(request, item, "get_lab") for item in LABS]

    @app.get("/labs/{record_id}", response_model=Lab, tags=["university"])
    async def get_lab(record_id: str, request: Request) -> dict[str, Any]:
        return _as_response(request, _find_record(LABS, record_id), "get_lab")

    @app.get("/positions", response_model=list[Position], tags=["university"])
    async def list_positions(request: Request) -> list[dict[str, Any]]:
        return [_as_response(request, item, "get_position") for item in POSITIONS]

    @app.get("/positions/{record_id}", response_model=Position, tags=["university"])
    async def get_position(record_id: str, request: Request) -> dict[str, Any]:
        return _as_response(request, _find_record(POSITIONS, record_id), "get_position")

    return app


app = create_app()
