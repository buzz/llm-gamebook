"""E2E tests for model configuration: creation, editing, deletion, and reset.

These exercise the real user flows in ``ModelConfigForm`` (``/model-config/new``
and ``/model-config/<id>``) against the real backend, including the ``/api``
proxy of the Vite dev server.
"""

import json
import re
import uuid
from typing import cast

from playwright.sync_api import APIRequestContext, Page, expect

MODEL_CONFIGS_API = "/api/model-configs/"

MODEL_CONFIG_EDIT_URL = re.compile(r"/model-config/[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}$")


def _unique(prefix: str) -> str:
    """Return ``prefix`` with a unique suffix, so tests never collide."""
    return f"{prefix}-{uuid.uuid4().hex[:8]}"


def _create_model_config_via_api(
    request: APIRequestContext, *, name: str, model_name: str
) -> dict[str, object]:
    """Create a model config directly through the API (test setup only)."""
    response = request.post(
        MODEL_CONFIGS_API,
        data=json.dumps({
            "name": name,
            "provider": "openai-compatible",
            "modelName": model_name,
            "contextWindow": 32_768,
            "maxTokens": 2000,
            "temperature": 1,
            "topP": 0.95,
            "presencePenalty": 0,
            "frequencyPenalty": 0,
        }),
        headers={"Content-Type": "application/json"},
    )
    assert response.ok, f"Failed to create model config via API: {response.text()}"
    return cast("dict[str, object]", response.json())


def test_create_model_via_form(page: Page) -> None:
    """A user can fill in the form and create a new model.

    Filling in Name and Model ID and clicking "Create" must persist the model
    and land the user on the new model's edit page, with the entered values
    shown in the form and the new model listed in the sidebar.
    """
    name = _unique("E2E-created model")
    model_id = _unique("e2e-model")
    console_errors: list[str] = []
    page.on(
        "console",
        lambda message: console_errors.append(message.text) if message.type == "error" else None,
    )

    page.goto("/model-config/new")
    expect(page.get_by_role("heading", name="Create Model")).to_be_visible()

    # Provider defaults to "openai-compatible"; only Name and Model ID are
    # required on top of the defaults. (Labels include a required asterisk,
    # e.g. "Name *", so match on substring.)
    page.get_by_label("Name").fill(name)
    page.get_by_label("Model ID").fill(model_id)
    page.get_by_role("button", name="Create", exact=True).click()

    # The model is created: a success toast appears and the user is
    # redirected to the edit page of the new model.
    expect(page.get_by_text("Model config was created.", exact=True)).to_be_visible()
    expect(page).to_have_url(MODEL_CONFIG_EDIT_URL)
    expect(page.get_by_role("heading", name="Edit Model")).to_be_visible()

    # The form is prefilled with the values the user just entered.
    expect(page.get_by_label("Name")).to_have_value(name)
    expect(page.get_by_label("Model ID")).to_have_value(model_id)

    # The new model is reachable from the sidebar list.
    expect(page.get_by_role("link", name=name)).to_be_visible()

    # No React "uncontrolled input to be controlled" warnings are logged.
    assert not any("uncontrolled" in error for error in console_errors), (
        f"Unexpected console errors: {console_errors}"
    )


def test_edit_model_prefills_values_and_saves_changes(page: Page) -> None:
    """The edit form shows the saved values, and edits persist after saving.

    Opening an existing model prefills the form (including Model ID), saving
    updated values updates the server, and the updated values are still shown
    after reloading the page.
    """
    initial_name = _unique("E2E-edit model")
    initial_model_id = _unique("e2e-model")
    config = _create_model_config_via_api(
        page.request, name=initial_name, model_name=initial_model_id
    )
    config_id = str(config["id"])

    page.goto(f"/model-config/{config_id}")
    expect(page.get_by_role("heading", name="Edit Model")).to_be_visible()

    # The form is prefilled with the saved values.
    expect(page.get_by_label("Name")).to_have_value(initial_name)
    expect(page.get_by_label("Model ID")).to_have_value(initial_model_id)

    # Change the values and save.
    updated_name = _unique("E2E-updated model")
    updated_model_id = _unique("e2e-model-updated")
    page.get_by_label("Name").fill(updated_name)
    page.get_by_label("Model ID").fill(updated_model_id)
    page.get_by_role("button", name="Save", exact=True).click()

    expect(page.get_by_text("Model config was updated.", exact=True)).to_be_visible()

    # The updated values survive a reload.
    page.reload()
    expect(page.get_by_label("Name")).to_have_value(updated_name)
    expect(page.get_by_label("Model ID")).to_have_value(updated_model_id)

    # The server persisted the update.
    response = page.request.get(f"{MODEL_CONFIGS_API}{config_id}")
    assert response.ok, f"Failed to fetch model config: {response.text()}"
    saved = response.json()
    assert saved["name"] == updated_name
    assert saved["modelName"] == updated_model_id


def test_delete_model(page: Page) -> None:
    """A user can delete a model from its edit page.

    Clicking Delete must remove the model (a success toast appears, the user
    is sent back home, the model disappears from the sidebar list, and the
    server no longer knows about it).
    """
    name = _unique("E2E-delete model")
    model_id = _unique("e2e-model")
    config = _create_model_config_via_api(page.request, name=name, model_name=model_id)
    config_id = str(config["id"])

    page.goto(f"/model-config/{config_id}")
    expect(page.get_by_role("heading", name="Edit Model")).to_be_visible()

    # Scope to the main area: the sidebar has a "Delete" action icon too.
    page.locator("main").get_by_role("button", name="Delete", exact=True).click()

    expect(page.get_by_text("Model config was deleted.", exact=True)).to_be_visible()

    # The user is redirected to the home page.
    expect(page).to_have_url(re.compile(r"^https?://[^/]+/$"))
    expect(page.get_by_role("heading", name="Gamebooks")).to_be_visible()

    # The model is gone from the sidebar list and from the server.
    expect(page.get_by_role("link", name=name)).to_have_count(0)
    response = page.request.get(f"{MODEL_CONFIGS_API}{config_id}")
    assert response.status == 404, f"Expected 404, got {response.status}"


def test_reset_advanced_values(page: Page) -> None:
    """'Reset values' restores the advanced settings sliders to their defaults."""
    page.goto("/model-config/new")
    expect(page.get_by_role("heading", name="Create Model")).to_be_visible()

    # Open the advanced settings and change every slider.
    page.get_by_role("switch", name="Advanced settings").click()

    page.get_by_label("Max. tokens").fill("3000")
    page.get_by_label("Temperature").fill("0.5")
    page.get_by_label("Top-p").fill("0.7")
    page.get_by_label("Presence penalty").fill("1")
    page.get_by_label("Frequency penalty").fill("2")

    expect(page.get_by_label("Max. tokens")).to_have_value("3000")
    expect(page.get_by_label("Temperature")).to_have_value("0.5")
    expect(page.get_by_label("Top-p")).to_have_value("0.7")
    expect(page.get_by_label("Presence penalty")).to_have_value("1")
    expect(page.get_by_label("Frequency penalty")).to_have_value("2")

    page.get_by_role("button", name="Reset values", exact=True).click()

    # The defaults are restored.
    expect(page.get_by_label("Max. tokens")).to_have_value("2000")
    expect(page.get_by_label("Temperature")).to_have_value("1")
    expect(page.get_by_label("Top-p")).to_have_value("0.95")
    expect(page.get_by_label("Presence penalty")).to_have_value("0")
    expect(page.get_by_label("Frequency penalty")).to_have_value("0")
