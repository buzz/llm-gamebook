from collections.abc import AsyncIterator
from pathlib import Path

import pytest
from pydantic_ai.models import Model
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession as AsyncDbSession

from llm_gamebook.db.models import Message, ModelConfig, Part, Session
from llm_gamebook.db.models.message import MessageKind
from llm_gamebook.db.models.part import PartKind
from llm_gamebook.engine.engine import StoryEngine
from llm_gamebook.message_bus import MessageBus
from llm_gamebook.providers import ModelProvider
from llm_gamebook.story.project import Project
from llm_gamebook.story.state import StoryState


@pytest.fixture
def examples_path() -> Path:
    return Path(__file__).parent.parent.parent / "examples"


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
async def message_bus() -> AsyncIterator[MessageBus]:
    async with MessageBus() as bus:
        yield bus


@pytest.fixture
def story_state(project: Project) -> StoryState:
    return StoryState(project)


@pytest.fixture
async def story_engine(
    session: Session, test_model: Model, story_state: StoryState, message_bus: MessageBus
) -> StoryEngine:
    return StoryEngine(session.id, test_model, story_state, message_bus, stream_debounce=0.0)


@pytest.fixture
async def sample_message_with_parts(db_session: AsyncDbSession, session: Session) -> Message:
    msg = Message(
        kind=MessageKind.REQUEST,
        session=session,
        model_name=None,
        finish_reason=None,
    )
    db_session.add(msg)
    await db_session.flush()

    parts = [
        Part(
            part_kind=PartKind.USER_PROMPT,
            content="Hello, world!",
            timestamp=None,
            tool_name=None,
            tool_call_id=None,
            args=None,
        ),
        Part(
            part_kind=PartKind.TEXT,
            content="This is a test message.",
            timestamp=None,
            tool_name=None,
            tool_call_id=None,
            args=None,
        ),
    ]
    for part in parts:
        part.message_id = msg.id
        db_session.add(part)

    await db_session.commit()
    await db_session.refresh(msg)
    return msg
