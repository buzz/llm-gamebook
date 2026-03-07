from collections.abc import AsyncIterator
from datetime import UTC, datetime

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
from llm_gamebook.story import Project, ProjectManager, StoryContext


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
def project_manager(tmp_path_factory: pytest.TempPathFactory) -> ProjectManager:
    tmp_path = tmp_path_factory.mktemp("local_projects")
    return ProjectManager(local_projects_path=tmp_path)


@pytest.fixture
def project(project_manager: ProjectManager) -> Project:
    project_def = project_manager.get_project("llm-gamebook/broken-bulb")
    return Project.from_definition(project_def)


@pytest.fixture
async def session(
    db_session: AsyncDbSession, model_config: ModelConfig, project: Project
) -> Session:
    session_obj = Session(title="Test Session", project_id=project.id, config=model_config)
    db_session.add(session_obj)
    await db_session.commit()
    await db_session.refresh(session_obj)
    return session_obj


@pytest.fixture
async def message(db_session: AsyncDbSession, session: Session) -> Message:
    msg = Message(
        kind=MessageKind.REQUEST,
        session=session,
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
def story_context(project: Project) -> StoryContext:
    return StoryContext(project)


@pytest.fixture
async def story_engine(
    session: Session, test_model: Model, story_context: StoryContext, message_bus: MessageBus
) -> StoryEngine:
    return StoryEngine(session.id, test_model, story_context, message_bus, stream_debounce=0.0)


@pytest.fixture
async def sample_message_with_parts(db_session: AsyncDbSession, session: Session) -> Message:
    msg = Message(
        kind=MessageKind.REQUEST,
        session=session,
    )
    db_session.add(msg)
    await db_session.flush()

    now = datetime.now(UTC)
    parts = [
        Part(
            kind=PartKind.USER_PROMPT,
            content="Hello, world!",
            timestamp=now,
            tool_name=None,
            tool_call_id=None,
            args=None,
        ),
        Part(
            kind=PartKind.TEXT,
            content="This is a test message.",
            timestamp=now,
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
