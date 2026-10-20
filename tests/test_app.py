from fastapi.testclient import TestClient

from app.main import create_app


def test_api_boots_with_environment_configuration(monkeypatch):
    monkeypatch.setenv("GAME_APP_NAME", "Test Football App")
    with TestClient(create_app()) as client:
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}
        schema = client.get("/openapi.json").json()
        assert schema["info"]["title"] == "Test Football App"
