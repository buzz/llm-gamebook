"""Architectural boundary rules.

This file defines rules to enforce clean separation between layers.
"""

from pytest_archon import archrule


def test_db() -> None:
    (
        archrule("'llm_gamebook.db' allowed imports")
        .match("*")
        .should_not_import("llm_gamebook.engine.*")
        .should_not_import("llm_gamebook.message_bus.*")
        .should_not_import("llm_gamebook.story.*")
        .should_not_import("llm_gamebook.tui.*")
        .should_not_import("llm_gamebook.web.*")
        .check("llm_gamebook.db")
    )


def test_engine() -> None:
    (
        archrule("'llm_gamebook.engine' allowed imports")
        .match("*")
        .should_not_import("llm_gamebook.tui.*")
        .should_not_import("llm_gamebook.web.*")
        .check("llm_gamebook.engine")
    )


def test_message_bus() -> None:
    (
        archrule("'llm_gamebook.message_bus' has no dependencies")
        .match("*")
        .should_not_import("llm_gamebook.db.*")
        .should_not_import("llm_gamebook.engine.*")
        .should_not_import("llm_gamebook.story.*")
        .should_not_import("llm_gamebook.tui.*")
        .should_not_import("llm_gamebook.web.*")
        .check("llm_gamebook.message_bus")
    )


def test_story() -> None:
    (
        archrule("'llm_gamebook.story' allowed imports")
        .match("*")
        .should_not_import("llm_gamebook.db.*")
        .should_not_import("llm_gamebook.engine.*")
        .should_not_import("llm_gamebook.tui.*")
        .should_not_import("llm_gamebook.web.*")
        .check("llm_gamebook.story")
    )


def test_tui() -> None:
    (
        archrule("'llm_gamebook.tui' allowed imports")
        .match("*")
        .should_not_import("llm_gamebook.web.*")
        .check("llm_gamebook.tui")
    )


def test_web() -> None:
    (
        archrule("'llm_gamebook.web' allowed imports")
        .match("*")
        .should_not_import("llm_gamebook.tui.*")
        .check("llm_gamebook.web")
    )


def test_core() -> None:
    (
        archrule("'llm_gamebook' core modules allowed imports")
        .match("llm_gamebook.constants")
        .match("llm_gamebook.logger")
        .match("llm_gamebook.providers")
        .match("llm_gamebook.utils")
        .should_not_import("llm_gamebook.db.*")
        .should_not_import("llm_gamebook.engine.*")
        .should_not_import("llm_gamebook.message_bus.*")
        .should_not_import("llm_gamebook.story.*")
        .should_not_import("llm_gamebook.tui.*")
        .should_not_import("llm_gamebook.web.*")
        .check("llm_gamebook")
    )


def test_main() -> None:
    (
        archrule("'llm_gamebook.main' allowed imports")
        .match("llm_gamebook.main")
        .should_not_import("llm_gamebook.db.*")
        .should_not_import("llm_gamebook.engine.*")
        .should_not_import("llm_gamebook.message_bus.*")
        .should_not_import("llm_gamebook.story.*")
        .check("llm_gamebook", only_direct_imports=True)
    )
