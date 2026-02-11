from collections.abc import AsyncIterator
from pathlib import Path
from typing import TYPE_CHECKING

import pytest
from pydantic_ai.models.test import TestModel
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession as AsyncDbSession

from llm_gamebook.db.models import Message, ModelConfig, Session
from llm_gamebook.db.models.message import MessageKind
from llm_gamebook.engine.engine import StoryEngine
from llm_gamebook.engine.manager import EngineManager
from llm_gamebook.engine.session_adapter import SessionAdapter
from llm_gamebook.message_bus import MessageBus
from llm_gamebook.providers import ModelProvider
from llm_gamebook.story.project import Project
from llm_gamebook.story.state import StoryState

if TYPE_CHECKING:
    from llm_gamebook.story.entity import EntityType


@pytest.fixture
def examples_path() -> Path:
    return Path(__file__).parent.parent.parent.parent / "examples"


@pytest.fixture
def project(examples_path: Path) -> Project:
    return Project.from_path(examples_path / "broken-bulb")


@pytest.fixture
async def db_engine() -> AsyncIterator[AsyncEngine]:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    try:
        yield engine
    finally:
        await engine.dispose()


@pytest.fixture
async def db_session(db_engine: AsyncEngine) -> AsyncIterator[AsyncDbSession]:
    async with AsyncDbSession(db_engine, expire_on_commit=False) as session:
        yield session


@pytest.fixture
async def model_config(db_session: AsyncDbSession) -> ModelConfig:
    config = ModelConfig(
        name="Test Config",
        provider=ModelProvider.OPENAI_COMPATIBLE,
        model_name="gpt-4",
        base_url="http://localhost:5001/v1",
        api_key="test-key-12345",
        context_window=4096,
        max_tokens=1024,
        temperature=0.7,
        top_p=0.9,
        presence_penalty=0.0,
        frequency_penalty=0.0,
    )
    db_session.add(config)
    await db_session.commit()
    await db_session.refresh(config)
    return config


@pytest.fixture
async def session(db_session: AsyncDbSession, model_config: ModelConfig) -> Session:
    session_obj = Session(title="Test Session", config=model_config)
    db_session.add(session_obj)
    await db_session.commit()
    await db_session.refresh(session_obj)
    return session_obj


@pytest.fixture
async def message(db_session: AsyncDbSession, session: Session) -> Message:
    msg = Message(
        kind=MessageKind.REQUEST,
        session=session,
        model_name=None,
        finish_reason=None,
    )
    db_session.add(msg)
    await db_session.commit()
    await db_session.refresh(msg)
    return msg


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
                "functions": [
                    {
                        "name": "transition",
                        "description": "Transition to another node",
                        "target": "transition",
                        "properties": {"to": "The node to transition to"},
                    }
                ],
                "entities": [
                    {
                        "id": "test_graph",
                        "name": "Test Graph",
                        "description": "A test graph",
                        "node_ids": ["node_a", "node_b"],
                        "current_node_id": "node_a",
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
                        "enabled": {"value": True},
                        "edge_ids": ["node_b"],
                    },
                    {
                        "id": "node_b",
                        "name": "Node B",
                        "description": "Second node",
                        "enabled": {"value": False},
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
def story_state(simple_project: Project) -> StoryState:
    return StoryState(simple_project)


@pytest.fixture
async def message_bus() -> AsyncIterator[MessageBus]:
    async with MessageBus() as bus:
        yield bus


@pytest.fixture
async def engine_manager(message_bus: MessageBus) -> AsyncIterator[EngineManager]:
    async with EngineManager(message_bus) as manager:
        yield manager


@pytest.fixture
def test_model() -> TestModel:
    return TestModel(custom_output_text="Test response")


@pytest.fixture
async def story_engine(
    session: Session, test_model: TestModel, story_state: StoryState, message_bus: MessageBus
) -> StoryEngine:
    return StoryEngine(session.id, test_model, story_state, message_bus, stream_debounce=0.0)


@pytest.fixture
def session_adapter(
    session: Session, story_state: StoryState, message_bus: MessageBus
) -> SessionAdapter:
    return SessionAdapter(session.id, story_state, message_bus)
