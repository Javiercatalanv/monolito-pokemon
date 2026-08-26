"""Tests del endpoint de estado del sistema."""

from datetime import UTC, datetime

from fastapi.testclient import TestClient

from app.core.config import settings


def test_health_is_reachable(client: TestClient, api_prefix: str):
    """Regresion: el router de health no estaba registrado y devolvia 404."""
    response = client.get(f"{api_prefix}/health")

    assert response.status_code == 200


def test_health_reports_project_identity(client: TestClient, api_prefix: str):
    body = client.get(f"{api_prefix}/health").json()

    assert body["status"] == "online"
    assert body["app_name"] == settings.PROJECT_NAME
    assert body["version"] == settings.VERSION


def test_health_timestamp_is_timezone_aware_and_recent(client: TestClient, api_prefix: str):
    body = client.get(f"{api_prefix}/health").json()

    timestamp = datetime.fromisoformat(body["timestamp"])
    assert timestamp.tzinfo is not None, "el timestamp debe venir con zona horaria"
    assert abs((datetime.now(UTC) - timestamp).total_seconds()) < 60


def test_health_is_documented_in_openapi(client: TestClient, api_prefix: str):
    schema = client.get(f"{api_prefix}/openapi.json").json()

    assert f"{api_prefix}/health" in schema["paths"]
