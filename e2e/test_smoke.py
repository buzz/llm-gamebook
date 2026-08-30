"""Smoke test: the full app (backend + frontend) boots and renders the home page."""

from playwright.sync_api import Page, expect


def test_home_page_loads(page: Page) -> None:
    page.goto("/")

    expect(page).to_have_title("LLM Gamebook")
    expect(page.get_by_role("heading", name="Gamebooks")).to_be_visible()
