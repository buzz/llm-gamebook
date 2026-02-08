from fastapi.testclient import TestClient

from llm_gamebook.main import app

client = TestClient(app)  # TODO: use proper fixture


async def test_create_model_config():
    model_data = {
        "name": "Test Model",
        "provider": "openai",
        "model_name": "gpt-4",
        "base_url": "https://api.openai.com/v1",
        "api_key": "test-key",
    }
    response = client.post("/api/model-configs/", json=model_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Model"
    assert data["provider"] == "openai"
    assert data["model_name"] == "gpt-4"
    assert "id" in data


async def test_read_model_configs():
    response = client.get("/api/model-configs/")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert "count" in data
    assert isinstance(data["data"], list)


async def test_read_model_config():
    model_data = {
        "name": "Test Model",
        "provider": "openai",
        "model_name": "gpt-4",
    }
    create_response = client.post("/api/model-configs/", json=model_data)
    assert create_response.status_code == 200
    config_id = create_response.json()["id"]

    response = client.get(f"/api/model-configs/{config_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == config_id
    assert data["name"] == "Test Model"


async def test_update_model_config():
    model_data = {
        "name": "Original Name",
        "provider": "openai",
        "model_name": "gpt-4",
    }
    create_response = client.post("/api/model-configs/", json=model_data)
    assert create_response.status_code == 200
    config_id = create_response.json()["id"]

    update_data = {"name": "Updated Name"}
    response = client.put(f"/api/model-configs/{config_id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Name"


async def test_delete_model_config():
    model_data = {
        "name": "To Delete",
        "provider": "ollama",
        "model_name": "llama3",
    }
    create_response = client.post("/api/model-configs/", json=model_data)
    assert create_response.status_code == 200
    config_id = create_response.json()["id"]

    response = client.delete(f"/api/model-configs/{config_id}")
    assert response.status_code == 200

    get_response = client.get(f"/api/model-configs/{config_id}")
    assert get_response.status_code == 404


async def test_list_providers():
    response = client.get("/api/model-configs/providers/")
    assert response.status_code == 200
    data = response.json()
    assert "providers" in data
    providers = [p["value"] for p in data["providers"]]
    assert "openai" in providers
    assert "ollama" in providers
    assert "groq" in providers
    assert "deepseek" in providers
    assert "mistral" in providers
    assert "openrouter" in providers
