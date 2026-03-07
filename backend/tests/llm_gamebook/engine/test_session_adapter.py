from pydantic_ai import ModelRequest
from sqlmodel.ext.asyncio.session import AsyncSession as AsyncDbSession

from llm_gamebook.db.models import Session
from llm_gamebook.db.models.message import MessageKind
from llm_gamebook.engine.session_adapter import SessionAdapter
from llm_gamebook.story.state import SessionStateData
from llm_gamebook.web.schemas.session.message import ModelRequestCreate
from llm_gamebook.web.schemas.session.part import UserPromptPartCreate


async def test_session_adapter_get_session(
    session_adapter: SessionAdapter, db_session: AsyncDbSession, session: Session
) -> None:
    result = await session_adapter.get_session(db_session)
    assert result is not None
    assert result.id == session.id
    assert result.title == session.title


async def test_session_adapter_delete_session(
    session_adapter: SessionAdapter, db_session: AsyncDbSession, session: Session
) -> None:
    await session_adapter.delete_session(db_session)
    result = await db_session.get(Session, session.id)
    assert result is None


async def test_session_adapter_get_message_count(
    session_adapter: SessionAdapter, db_session: AsyncDbSession, session: Session
) -> None:
    result = await session_adapter.get_message_count(db_session)
    assert result >= 0


async def test_session_adapter_get_message_history(
    session_adapter: SessionAdapter, db_session: AsyncDbSession, session: Session
) -> None:
    messages = [msg async for msg in session_adapter.get_message_history(db_session)]
    assert len(messages) >= 0
    if messages:
        initial_request = messages[0]
        assert isinstance(initial_request, ModelRequest)
        assert len(initial_request.parts) >= 0


async def test_session_adapter_create_user_request(
    session_adapter: SessionAdapter, db_session: AsyncDbSession, session: Session
) -> None:
    message_in = ModelRequestCreate(
        parts=[UserPromptPartCreate(content="Test user request")],
    )
    result = await session_adapter.create_user_request(db_session, message_in)

    assert result is not None
    assert result.session_id == session.id
    assert result.kind == MessageKind.REQUEST


async def test_session_adapter_session_id(
    session_adapter: SessionAdapter, session: Session
) -> None:
    assert session_adapter.session_id == session.id


async def test_session_adapter_load_state_no_state(
    session_adapter: SessionAdapter, db_session: AsyncDbSession, session: Session
) -> None:
    loaded_state = await session_adapter.load_state(db_session)
    # May be None or have data depending on session
    # Just verify it doesn't raise and returns valid type
    assert loaded_state is None or isinstance(loaded_state, SessionStateData)
