from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_root():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["message"] == "Welcome to CodePulse API"


def test_application_health():
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    assert response.json()["application"] == "CodePulse"


def test_database_health():
    response = client.get("/api/v1/health/db")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    assert response.json()["connection"] == "successful"