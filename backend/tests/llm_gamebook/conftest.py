from collections.abc import AsyncIterator
from typing import TYPE_CHECKING

import pytest
from pydantic_ai import Agent
from pydantic_ai.models.test import TestModel

from llm_gamebook.db.models import Session
from llm_gamebook.engine.manager import EngineManager
from llm_gamebook.engine.session_adapter import SessionAdapter
from llm_gamebook.message_bus import MessageBus
from llm_gamebook.story.project import Project
from llm_gamebook.story.state import StoryState

if TYPE_CHECKING:
    from llm_gamebook.story.entity import EntityType


@pytest.fixture
def simple_project() -> Project:
    return Project.from_data({
        "title": "Test Project",
        "description": "A test project",
        "entity_types": [
            {
                "id": "TestGraph",
                "name": "Test Graph",
                "traits": [
                    "described",
                    {"name": "graph", "node_type_id": "TestNode"},
                ],
                "entities": [
                    {
                        "id": "test_graph",
                        "name": "Test Graph",
                        "description": "A test graph",
                        "node_ids": ["node_a", "node_b", "node_c", "node_d"],
                        "current_node_id": "node_a",
                        "functions": [
                            {
                                "name": "transition",
                                "description": "Transition to another node",
                                "target": "transition",
                                "properties": {"to": "The node to transition to"},
                            }
                        ],
                    }
                ],
            },
            {
                "id": "TestNode",
                "name": "Test Node",
                "traits": ["described", "graph_node"],
                "entities": [
                    {
                        "id": "node_a",
                        "name": "Node A",
                        "description": "First node",
                        "enabled": True,
                        "edge_ids": ["node_b"],
                    },
                    {
                        "id": "node_b",
                        "name": "Node B",
                        "description": "Second node",
                        "enabled": False,
                        "edge_ids": [],
                    },
                    {
                        "id": "node_c",
                        "name": "Node C",
                        "description": "Third node",
                        "enabled": "test_graph.current_node_id == 'node_a'",
                        "edge_ids": [],
                    },
                    {
                        "id": "node_d",
                        "name": "Node D",
                        "description": "Fourth node",
                        "enabled": "test_graph.current_node_id == 'node_b'",
                        "edge_ids": [],
                    },
                ],
            },
        ],
    })


@pytest.fixture
def simple_entity_type(simple_project: Project) -> "EntityType":
    return simple_project.get_entity_type("TestNode")


@pytest.fixture
async def engine_manager(message_bus: MessageBus) -> AsyncIterator[EngineManager]:
    async with EngineManager(message_bus) as manager:
        yield manager


@pytest.fixture
def test_model() -> TestModel:
    return TestModel(custom_output_text="Test response")


@pytest.fixture
def test_agent(test_model: TestModel, story_state: StoryState) -> Agent[StoryState, str]:
    return Agent(
        test_model,
        deps_type=StoryState,
        instructions="You are a test agent.",
        output_type=str,
        tools=list(story_state.get_tools()),
    )


@pytest.fixture
def session_adapter(
    session: Session, story_state: StoryState, message_bus: MessageBus
) -> SessionAdapter:
    return SessionAdapter(session.id, story_state, message_bus)
