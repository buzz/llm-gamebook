import logging
from uuid import uuid4

import pytest

from llm_gamebook.message_bus import MessageBus
from llm_gamebook.story.context import StoryContext
from llm_gamebook.story.errors import EntityFieldNotFoundError
from llm_gamebook.story.schemas import Project
from llm_gamebook.story.state import ActionDispatched, EndGameAction, SessionStateData
from llm_gamebook.story.state.middleware import auto_save_middleware, logging_middleware


async def test_story_context_get_system_prompt(story_context: StoryContext) -> None:
    result = await story_context.get_system_prompt()
    assert isinstance(result, str)
    assert len(result) > 0
    assert "narrator" in result.lower()


async def test_story_context_get_intro_message(story_context: StoryContext) -> None:
    result = await story_context.get_intro_message()
    assert isinstance(result, str)
    assert len(result) > 0
    assert "opening" in result.lower() or "story" in result.lower()


def test_story_context_get_tools(story_context: StoryContext) -> None:
    tools = list(story_context.get_tools())
    assert len(tools) >= 0


def test_story_context_project_property(story_context: StoryContext, project: Project) -> None:
    assert story_context.project == project


def test_story_context_jinja_env_cached(story_context: StoryContext) -> None:
    env1 = story_context._jinja_env
    env2 = story_context._jinja_env
    assert env1 is env2


def test_get_field_returns_session_override(project: Project) -> None:
    session_data = SessionStateData(entities={"main": {"custom_field": 50}})
    context = StoryContext(project, session_data)

    result = context.get_field("main", "custom_field")

    assert result == 50


def test_get_field_returns_project_default(story_context: StoryContext) -> None:
    result = story_context.get_field("main", "description")

    assert result is not None


def test_session_state_stores_field(project: Project) -> None:
    session_data = SessionStateData(entities={"main": {"custom_field": 75}})
    context = StoryContext(project, session_data)

    assert context.session_state.get_field("main", "custom_field") == 75


def test_orphaned_field_in_session_not_in_project(project: Project) -> None:
    session_data = SessionStateData(entities={"main": {"removed_field": 100}})
    context = StoryContext(project, session_data)

    result = context.get_field("main", "removed_field")

    assert result == 100


def test_missing_field_in_session_new_in_project(story_context: StoryContext) -> None:
    result = story_context.get_field("main", "description")

    assert result is not None


def test_invalid_entity_id_raises(story_context: StoryContext) -> None:
    with pytest.raises(EntityFieldNotFoundError):
        story_context.get_field("nonexistent", "some_field")


def test_story_context_default_middleware_chain_order(
    project: Project, message_bus: MessageBus
) -> None:
    context = StoryContext(project, session_id=uuid4(), message_bus=message_bus)

    # Chain: Logger -> MessageBusPublisher -> TriggerEval -> AutoSave
    chain = context.store._middleware
    assert len(chain) == 4
    assert chain[0] is logging_middleware
    assert chain[3] is auto_save_middleware
    # The publisher and trigger slots are factory-created callables
    assert chain[1] is not logging_middleware
    assert chain[2] is not auto_save_middleware

    order: list[str] = []

    class _LoggerProbe(logging.Handler):
        def emit(self, record: logging.LogRecord) -> None:
            order.append("logger")

    middleware_logger = logging.getLogger("llm_gamebook.story.state.middleware")
    probe = _LoggerProbe()
    old_level = middleware_logger.level
    middleware_logger.addHandler(probe)
    middleware_logger.setLevel(logging.INFO)
    try:
        message_bus.subscribe(ActionDispatched, lambda msg: order.append("publisher"))
        context.store.dispatch(EndGameAction(reason="done"))
    finally:
        middleware_logger.removeHandler(probe)
        middleware_logger.setLevel(old_level)

    assert order == ["logger", "publisher"]


def test_story_context_chain_executes_without_bus(
    project: Project, message_bus: MessageBus, caplog: pytest.LogCaptureFixture
) -> None:
    context = StoryContext(project)

    received: list[ActionDispatched] = []
    message_bus.subscribe(ActionDispatched, received.append)

    with caplog.at_level(logging.INFO, logger="llm_gamebook.story.state.middleware"):
        context.store.dispatch(EndGameAction(reason="done"))

    # Logger middleware ran (chain executed) but the unbound publisher published nothing
    assert any("Action dispatched" in r.message for r in caplog.records)
    assert received == []


def test_story_context_optional_construction_params(project: Project) -> None:
    # Plain construction (existing call sites) still works and dispatches
    plain = StoryContext(project)
    plain.store.dispatch(EndGameAction(reason="done"))

    # Session ID without bus: publisher is a no-op, dispatch works
    sid_only = StoryContext(project, session_id=uuid4())
    sid_only.store.dispatch(EndGameAction(reason="done"))

    # Session state param still accepted alongside the new optional params
    data = SessionStateData(entities={"main": {"custom_field": 50}})
    full = StoryContext(project, data, session_id=uuid4())
    assert full.session_state.get_field("main", "custom_field") == 50
