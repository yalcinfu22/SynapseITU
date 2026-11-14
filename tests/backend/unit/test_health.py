from fastapi.testclient import TestClient

from app.main import create_app


def test_health_endpoint_reports_ok():
    client = TestClient(create_app())
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok", "service": "backend"}


def test_openapi_document_is_generated():
    """WBS-16.3 compares the API specification with this generated document."""
    client = TestClient(create_app())
    assert client.get("/openapi.json").json()["info"]["title"] == "SynapseITU API"
