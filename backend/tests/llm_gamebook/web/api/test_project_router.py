from fastapi.testclient import TestClient


def test_list_projects_empty(client: TestClient) -> None:
    response = client.get("/api/projects/?source=local")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert "count" in data
    assert data["data"] == []
    assert data["count"] == 0


def test_list_projects_all(client: TestClient) -> None:
    response = client.get("/api/projects/")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert "count" in data
    assert isinstance(data["data"], list)
    assert data["count"] >= 1
    project_ids = [p["id"] for p in data["data"]]
    assert "llm-gamebook/broken-bulb" in project_ids


def test_list_projects_example_only(client: TestClient) -> None:
    response = client.get("/api/projects/?source=example")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert "count" in data
    assert data["count"] >= 1
    for project in data["data"]:
        assert project["source"] == "example"
    project_ids = [p["id"] for p in data["data"]]
    assert "llm-gamebook/broken-bulb" in project_ids


def test_list_projects_local_only(client: TestClient) -> None:
    response = client.get("/api/projects/?source=local")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert "count" in data
    for project in data["data"]:
        assert project["source"] == "local"


def test_get_project_found(client: TestClient) -> None:
    response = client.get("/api/projects/llm-gamebook/broken-bulb")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "llm-gamebook/broken-bulb"
    assert data["title"] == "Broken Bulb"
    assert data["source"] == "example"
    assert "entity_types" in data


def test_get_project_not_found(client: TestClient) -> None:
    response = client.get("/api/projects/namespace/nonexistent")
    assert response.status_code == 404
    assert response.json()["detail"] == "Project not found"


def test_create_project_success(client: TestClient) -> None:
    project_data = {
        "id": "test-namespace/test-project",
        "source": "local",
        "title": "Test Project",
        "description": "A test project",
    }
    response = client.post("/api/projects/", json=project_data)
    assert response.status_code == 201
    data = response.json()
    assert data["id"] == "test-namespace/test-project"
    assert data["title"] == "Test Project"
    assert data["source"] == "local"


def test_create_project_already_exists(client: TestClient) -> None:
    project_data = {
        "id": "test-namespace/duplicate-project",
        "source": "local",
        "title": "Duplicate Project",
        "description": "A duplicate project",
    }
    response = client.post("/api/projects/", json=project_data)
    assert response.status_code == 201

    response = client.post("/api/projects/", json=project_data)
    assert response.status_code == 409
    assert "already exists" in response.json()["detail"]


def test_create_project_invalid_id(client: TestClient) -> None:
    project_data = {
        "id": "Invalid ID",
        "source": "local",
        "title": "Invalid Project",
        "description": "A project with invalid ID",
    }
    response = client.post("/api/projects/", json=project_data)
    assert response.status_code == 422


def test_delete_project_success(client: TestClient) -> None:
    project_data = {
        "id": "test-namespace/to-delete",
        "source": "local",
        "title": "To Delete",
        "description": "A project to delete",
    }
    create_response = client.post("/api/projects/", json=project_data)
    assert create_response.status_code == 201

    response = client.delete("/api/projects/test-namespace/to-delete")
    assert response.status_code == 200
    assert response.json()["message"] == "Project deleted successfully"

    get_response = client.get("/api/projects/test-namespace/to-delete")
    assert get_response.status_code == 404


def test_delete_project_not_found(client: TestClient) -> None:
    response = client.delete("/api/projects/namespace/nonexistent")
    assert response.status_code == 404
    assert response.json()["detail"] == "Project not found"


def test_delete_project_not_local(client: TestClient) -> None:
    response = client.delete("/api/projects/llm-gamebook/broken-bulb")
    assert response.status_code == 400
    assert "Can only delete local projects" in response.json()["detail"]


def test_get_project_image_found(client: TestClient) -> None:
    response = client.get("/api/projects/llm-gamebook/broken-bulb/image")
    assert response.status_code == 200
    assert response.content is not None
    assert len(response.content) > 0


def test_get_project_image_not_found(client: TestClient) -> None:
    response = client.get("/api/projects/namespace/nonexistent/image")
    assert response.status_code == 404
    assert response.json()["detail"] == "Project not found"


def test_get_project_image_no_image(client: TestClient) -> None:
    project_data = {
        "id": "test-namespace/no-image-project",
        "source": "local",
        "title": "No Image Project",
        "description": "A project without image",
    }
    response = client.post("/api/projects/", json=project_data)
    assert response.status_code == 201

    response = client.get("/api/projects/test-namespace/no-image-project/image")
    assert response.status_code == 404
    assert response.json()["detail"] == "Project has no image"
