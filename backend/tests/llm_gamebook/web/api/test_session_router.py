from fastapi.testclient import TestClient

from llm_gamebook.db.models import ModelConfig, Session


def test_read_sessions_empty(client: TestClient) -> None:
    response = client.get("/api/sessions/")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert "count" in data
    assert isinstance(data["data"], list)
    assert data["count"] == 0


def test_read_sessions_with_pagination(client: TestClient, model_config: ModelConfig) -> None:
    session_data = {"config_id": str(model_config.id), "title": "Test Session"}
    response = client.post("/api/sessions/", json=session_data)
    assert response.status_code == 200

    response = client.get("/api/sessions/?skip=0&limit=10")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert "count" in data
    assert isinstance(data["data"], list)
    assert data["count"] >= 1
    assert len(data["data"]) >= 1


def test_read_session_found(client: TestClient, model_config: ModelConfig) -> None:
    session_data = {"config_id": str(model_config.id), "title": "Test Session"}
    create_response = client.post("/api/sessions/", json=session_data)
    assert create_response.status_code == 200
    session_id = create_response.json()["id"]

    response = client.get(f"/api/sessions/{session_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == session_id
    assert data["title"] == "Test Session"


def test_read_session_not_found(client: TestClient) -> None:
    response = client.get("/api/sessions/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404


def test_create_session_success(client: TestClient, model_config: ModelConfig) -> None:
    session_data = {"config_id": str(model_config.id), "title": "New Session"}
    response = client.post("/api/sessions/", json=session_data)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "New Session"
    assert "id" in data
    assert data["config_id"] == str(model_config.id)


def test_create_session_model_config_not_found(client: TestClient) -> None:
    session_data = {"config_id": "00000000-0000-0000-0000-000000000000", "title": "Invalid Session"}
    response = client.post("/api/sessions/", json=session_data)
    assert response.status_code == 404


def test_update_session(client: TestClient, model_config: ModelConfig, session: Session) -> None:
    update_data = {
        "id": str(session.id),
        "config_id": str(model_config.id),
        "title": "Updated Title",
    }
    response = client.patch(f"/api/sessions/{session.id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Session updated successfully."


def test_create_model_request(client: TestClient, session: Session) -> None:
    request_data = {
        "kind": "request",
        "parts": [{"part_kind": "user-prompt", "content": "Hello"}],
    }
    response = client.post(f"/api/sessions/{session.id}/request", json=request_data)
    assert response.status_code == 200
    data = response.json()
    assert data["kind"] == "request"
    assert "id" in data
    assert len(data["parts"]) == 1
    assert data["parts"][0]["content"] == "Hello"


def test_delete_session(client: TestClient, session: Session) -> None:
    response = client.get(f"/api/sessions/{session.id}")
    assert response.status_code == 200

    response = client.delete(f"/api/sessions/{session.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Story session deleted successfully."

    response = client.get(f"/api/sessions/{session.id}")
    assert response.status_code == 404
