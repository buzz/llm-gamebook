from llm_gamebook.story.context import StoryContext
from llm_gamebook.story.project import Project
from llm_gamebook.story.session_state import SessionStateData


async def test_story_context_get_system_prompt(project: Project) -> None:
    story_context = StoryContext(project)
    result = await story_context.get_system_prompt()
    assert isinstance(result, str)
    assert len(result) > 0
    assert "narrator" in result.lower()


async def test_story_context_get_intro_message(project: Project) -> None:
    story_context = StoryContext(project)
    result = await story_context.get_intro_message()
    assert isinstance(result, str)
    assert len(result) > 0
    assert "opening" in result.lower() or "story" in result.lower()


def test_story_context_get_tools(project: Project) -> None:
    story_context = StoryContext(project)
    tools = list(story_context.get_tools())
    assert len(tools) >= 0


def test_story_context_project_property(project: Project) -> None:
    story_context = StoryContext(project)
    assert story_context.project == project


def test_story_context_jinja_env_cached(project: Project) -> None:
    story_context = StoryContext(project)
    env1 = story_context._jinja_env
    env2 = story_context._jinja_env
    assert env1 is env2


def test_get_effective_field_returns_session_override(project: Project) -> None:
    session_data = SessionStateData(entities={"main": {"custom_field": 50}})
    context = StoryContext(project, session_data)

    result = context.get_effective_field("main", "custom_field")

    assert result == 50


def test_get_effective_field_returns_project_default(project: Project) -> None:
    context = StoryContext(project)

    result = context.get_effective_field("main", "description")

    assert result is not None


def test_session_state_stores_field(project: Project) -> None:
    session_data = SessionStateData(entities={"main": {"custom_field": 75}})
    context = StoryContext(project, session_data)

    assert context.session_state.get_field("main", "custom_field") == 75


def test_orphaned_field_in_session_not_in_project(project: Project) -> None:
    session_data = SessionStateData(entities={"main": {"removed_field": 100}})
    context = StoryContext(project, session_data)

    result = context.get_effective_field("main", "removed_field")

    assert result == 100


def test_missing_field_in_session_new_in_project(project: Project) -> None:
    context = StoryContext(project)

    result = context.get_effective_field("main", "description")

    assert result is not None


def test_invalid_entity_id_returns_none(project: Project) -> None:
    context = StoryContext(project)

    result = context.get_effective_field("nonexistent", "some_field")

    assert result is None
