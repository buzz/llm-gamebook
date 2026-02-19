import pytest

from llm_gamebook.story.context import StoryContext
from llm_gamebook.story.errors import EntityFieldNotFoundError
from llm_gamebook.story.project import Project
from llm_gamebook.story.session_state import SessionStateData


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
