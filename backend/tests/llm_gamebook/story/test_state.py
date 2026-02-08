from llm_gamebook.story.project import Project
from llm_gamebook.story.state import StoryState


async def test_story_state_get_system_prompt(project: Project) -> None:
    story_state = StoryState(project)
    result = await story_state.get_system_prompt()
    assert isinstance(result, str)
    assert len(result) > 0
    assert "narrator" in result.lower()


async def test_story_state_get_intro_message(project: Project) -> None:
    story_state = StoryState(project)
    result = await story_state.get_intro_message()
    assert isinstance(result, str)
    assert len(result) > 0
    assert "opening" in result.lower() or "story" in result.lower()


def test_story_state_get_tools(project: Project) -> None:
    story_state = StoryState(project)
    tools = list(story_state.get_tools())
    assert len(tools) >= 0


def test_story_state_project_property(project: Project) -> None:
    story_state = StoryState(project)
    assert story_state.project == project


def test_story_state_jinja_env_cached(project: Project) -> None:
    story_state = StoryState(project)
    env1 = story_state._jinja_env
    env2 = story_state._jinja_env
    assert env1 is env2
