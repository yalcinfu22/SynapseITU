"""Contract and isolation tests for WBS-13.1 (FR-65 / US-55)."""

import pytest
from fastapi.testclient import TestClient

from app.dummy_university.main import create_app


@pytest.fixture
def client() -> TestClient:
    return TestClient(create_app())


def test_service_runs_independently(client: TestClient) -> None:
    assert client.get("/health").json() == {"status": "ok", "service": "dummy-university"}
    assert client.get("/openapi.json").json()["info"]["title"] == (
        "SynapseITU Dummy University API"
    )


@pytest.mark.parametrize("collection", ["programs", "labs", "positions"])
def test_list_endpoints_return_seed_data_with_working_source_urls(
    client: TestClient, collection: str
) -> None:
    response = client.get(f"/{collection}")
    assert response.status_code == 200
    records = response.json()
    assert len(records) >= 2
    assert len({record["id"] for record in records}) == len(records)

    for record in records:
        assert record["university_id"] == "demo-uni"
        assert record["name"]
        assert record["updated_at"]
        assert record["source_url"].endswith(f"/{collection}/{record['id']}")
        detail = client.get(record["source_url"])
        assert detail.status_code == 200
        assert detail.json() == record


@pytest.mark.parametrize("collection", ["programs", "labs", "positions"])
def test_unknown_record_returns_404(client: TestClient, collection: str) -> None:
    response = client.get(f"/{collection}/does-not-exist")
    assert response.status_code == 404
    assert response.json()["detail"] == "Record not found"


def test_positions_reference_existing_labs_and_programs(client: TestClient) -> None:
    labs = {lab["id"] for lab in client.get("/labs").json()}
    programs = {program["id"] for program in client.get("/programs").json()}

    for position in client.get("/positions").json():
        assert position["lab_id"] in labs
        assert position["program_id"] is None or position["program_id"] in programs
        assert position["status"] in ("open", "closed")
        assert position["application_deadline"]


def test_contract_schema_has_required_properties(client: TestClient) -> None:
    document = client.get("/openapi.json").json()
    for model in ("Program", "Lab", "Position"):
        schema = document["components"]["schemas"][model]
        assert schema["properties"]["source_url"]["type"] == "string"
        assert "id" in schema["required"]
