from fastapi.testclient import TestClient
from sqlmodel.ext.asyncio.session import AsyncSession as AsyncDbSession

from llm_gamebook.db.models import UserSettings
from llm_gamebook.db.models.user_settings import ChatView


async def test_get_settings_not_found_creates_defaults(client: TestClient) -> None:
    response = client.get("/api/settings/")
    assert response.status_code == 200
    data = response.json()
    assert data["chatView"] == "standard"
    assert data["enterSubmitsMessage"] is True


async def test_get_settings_returns_existing(
    client: TestClient, db_session: AsyncDbSession
) -> None:
    settings = UserSettings(id="settings", chat_view=ChatView.DETAILS, enter_submits_message=False)
    db_session.add(settings)
    await db_session.commit()

    response = client.get("/api/settings/")
    assert response.status_code == 200
    data = response.json()
    assert data["chatView"] == "details"
    assert data["enterSubmitsMessage"] is False


def test_put_settings_updates_full_object(client: TestClient) -> None:
    update_data = {"chatView": "debug", "enterSubmitsMessage": False}
    response = client.put("/api/settings/", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Settings updated successfully."

    get_response = client.get("/api/settings/")
    assert get_response.status_code == 200
    data = get_response.json()
    assert data["chatView"] == "debug"
    assert data["enterSubmitsMessage"] is False


def test_put_settings_overwrites_all_fields(client: TestClient) -> None:
    update_data = {"chatView": "standard"}
    response = client.put("/api/settings/", json=update_data)
    assert response.status_code == 200

    get_response = client.get("/api/settings/")
    assert get_response.status_code == 200
    data = get_response.json()
    assert data["chatView"] == "standard"
    assert data["enterSubmitsMessage"] is True
