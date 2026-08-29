from collections.abc import AsyncIterator

import pytest

from llm_gamebook.engine.engine import StoryEngine
from llm_gamebook.engine.manager import EngineManager
from llm_gamebook.message_bus import MessageBus

from .mocks.model import MockModel
from .mocks.player import MockPlayer


@pytest.fixture
def test_model() -> MockModel:
    return MockModel()


@pytest.fixture
def test_player(story_engine: StoryEngine) -> MockPlayer:
    return MockPlayer(story_engine)


@pytest.fixture
async def engine_manager(message_bus: MessageBus) -> AsyncIterator[EngineManager]:
    async with EngineManager(message_bus) as manager:
        yield manager
