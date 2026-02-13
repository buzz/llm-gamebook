from uuid import uuid4

from pydantic_ai import ModelRequest, ModelResponse, RequestUsage, TextPart, UserPromptPart
from sqlmodel.ext.asyncio.session import AsyncSession as AsyncDbSession

from llm_gamebook.db.models import Session
from llm_gamebook.db.models.message import MessageKind
from llm_gamebook.engine.session_adapter import SessionAdapter
from llm_gamebook.web.schema.session.message import ModelRequestCreate
from llm_gamebook.web.schema.session.part import UserPromptPartCreate


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
    result = await db_session.get(type(session), session.id)
    assert result is None


async def test_session_adapter_get_message_count(
    session_adapter: SessionAdapter, db_session: AsyncDbSession, session: Session
) -> None:
    result = await session_adapter.get_message_count(db_session)
    assert result == 0


async def test_session_adapter_get_message_history(
    session_adapter: SessionAdapter, db_session: AsyncDbSession, session: Session
) -> None:
    messages = [msg async for msg in session_adapter.get_message_history(db_session)]
    assert len(messages) == 1
    initial_request = messages[0]
    assert isinstance(initial_request, ModelRequest)
    assert len(initial_request.parts) == 1


async def test_session_adapter_append_messages(
    session_adapter: SessionAdapter, db_session: AsyncDbSession, session: Session
) -> None:
    model_request = ModelRequest(parts=[UserPromptPart(content="Test user message")])
    model_response = ModelResponse(
        parts=[TextPart(content="Test response")],
        model_name="gpt-4",
        usage=RequestUsage(input_tokens=5, output_tokens=5),
    )
    await session_adapter.append_messages(db_session, [model_request, model_response])

    count = await session_adapter.get_message_count(db_session)
    assert count == 2


async def test_session_adapter_append_messages_with_ids(
    session_adapter: SessionAdapter, db_session: AsyncDbSession, session: Session
) -> None:
    msg_id = uuid4()
    part_ids = [uuid4()]
    model_request = ModelRequest(parts=[UserPromptPart(content="Test user message")])
    await session_adapter.append_messages(
        db_session, [model_request], message_ids=[msg_id], part_ids=[part_ids]
    )

    count = await session_adapter.get_message_count(db_session)
    assert count == 1


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
