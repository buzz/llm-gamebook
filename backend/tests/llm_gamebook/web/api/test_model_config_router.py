from fastapi.testclient import TestClient


def test_create_model_config(client: TestClient) -> None:
    model_data = {
        "name": "Test Model",
        "provider": "openai",
        "model_name": "gpt-4",
        "base_url": "https://api.openai.com/v1",
        "api_key": "test-key",
        "context_window": 4096,
        "max_tokens": 1024,
        "temperature": 0.7,
        "top_p": 0.9,
        "presence_penalty": 0.0,
        "frequency_penalty": 0.0,
    }
    response = client.post("/api/model-configs/", json=model_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Model"
    assert data["provider"] == "openai"
    assert data["model_name"] == "gpt-4"
    assert "id" in data


def test_read_model_configs(client: TestClient) -> None:
    response = client.get("/api/model-configs/")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert "count" in data
    assert isinstance(data["data"], list)


def test_read_model_config(client: TestClient) -> None:
    model_data = {
        "name": "Test Model",
        "provider": "openai",
        "model_name": "gpt-4",
        "context_window": 4096,
        "max_tokens": 1024,
        "temperature": 0.7,
        "top_p": 0.9,
        "presence_penalty": 0.0,
        "frequency_penalty": 0.0,
    }
    create_response = client.post("/api/model-configs/", json=model_data)
    assert create_response.status_code == 200
    config_id = create_response.json()["id"]

    response = client.get(f"/api/model-configs/{config_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == config_id
    assert data["name"] == "Test Model"


def test_update_model_config(client: TestClient) -> None:
    model_data = {
        "name": "Original Name",
        "provider": "openai",
        "model_name": "gpt-4",
        "context_window": 4096,
        "max_tokens": 1024,
        "temperature": 0.7,
        "top_p": 0.9,
        "presence_penalty": 0.0,
        "frequency_penalty": 0.0,
    }
    create_response = client.post("/api/model-configs/", json=model_data)
    assert create_response.status_code == 200
    config_id = create_response.json()["id"]

    update_data = {
        "name": "Updated Name",
        "provider": "openai",
        "model_name": "gpt-4",
        "context_window": 4096,
        "max_tokens": 1024,
        "temperature": 0.7,
        "top_p": 0.9,
        "presence_penalty": 0.0,
        "frequency_penalty": 0.0,
    }
    response = client.put(f"/api/model-configs/{config_id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Model config updated successfully."

    get_response = client.get(f"/api/model-configs/{config_id}")
    assert get_response.status_code == 200
    assert get_response.json()["name"] == "Updated Name"


def test_delete_model_config(client: TestClient) -> None:
    model_data = {
        "name": "To Delete",
        "provider": "ollama",
        "model_name": "llama3",
        "context_window": 4096,
        "max_tokens": 1024,
        "temperature": 0.7,
        "top_p": 0.9,
        "presence_penalty": 0.0,
        "frequency_penalty": 0.0,
    }
    create_response = client.post("/api/model-configs/", json=model_data)
    assert create_response.status_code == 200
    config_id = create_response.json()["id"]

    response = client.delete(f"/api/model-configs/{config_id}")
    assert response.status_code == 200

    get_response = client.get(f"/api/model-configs/{config_id}")
    assert get_response.status_code == 404


def test_list_providers(client: TestClient) -> None:
    response = client.get("/api/model-configs/providers/")
    assert response.status_code == 200
    data = response.json()
    assert "openai" in data
    assert "ollama" in data
    assert "anthropic" in data
    assert "deepseek" in data
    assert "mistral" in data
    assert "openrouter" in data
