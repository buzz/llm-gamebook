import pytest

from llm_gamebook.engine.engine import StoryEngine

from .mocks.model import MockModel
from .mocks.player import MockPlayer


@pytest.fixture
def test_model() -> MockModel:
    return MockModel()


@pytest.fixture
def test_player(story_engine: StoryEngine) -> MockPlayer:
    return MockPlayer(story_engine)
