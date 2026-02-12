from datetime import UTC, datetime

from sqlmodel.ext.asyncio.session import AsyncSession as AsyncDbSession

from llm_gamebook.db.crud import message as message_crud
from llm_gamebook.db.models import Message, Session
from llm_gamebook.db.models.message import MessageKind


async def test_get_message_count(db_session: AsyncDbSession, session: Session) -> None:
    """Test counting messages for a session."""
    msg1 = Message(
        kind=MessageKind.REQUEST,
        session_id=session.id,
        timestamp=datetime.now(UTC),
        model_name=None,
    )
    msg2 = Message(
        kind=MessageKind.RESPONSE,
        session_id=session.id,
        timestamp=datetime.now(UTC),
        model_name=None,
    )

    await message_crud.create_message(db_session, msg1)
    await message_crud.create_message(db_session, msg2)

    count = await message_crud.get_message_count(db_session, session.id)

    assert count == 2


async def test_get_message_count_empty(db_session: AsyncDbSession, session: Session) -> None:
    """Test counting messages when session has no messages."""
    count = await message_crud.get_message_count(db_session, session.id)

    assert count == 0


async def test_get_messages(db_session: AsyncDbSession, session: Session) -> None:
    """Test retrieving messages for a session with ordering."""
    timestamp_earlier = datetime(2024, 1, 1, 12, 0, 0, tzinfo=UTC)
    timestamp_later = datetime(2024, 1, 1, 12, 1, 0, tzinfo=UTC)

    msg1 = Message(
        kind=MessageKind.REQUEST,
        session_id=session.id,
        timestamp=timestamp_earlier,
        model_name=None,
    )
    msg2 = Message(
        kind=MessageKind.RESPONSE, session_id=session.id, timestamp=timestamp_later, model_name=None
    )

    await message_crud.create_message(db_session, msg1)
    await message_crud.create_message(db_session, msg2)

    messages = await message_crud.get_messages(db_session, session.id)

    assert len(messages) == 2
    assert messages[0].id == msg2.id
    assert messages[1].id == msg1.id


async def test_get_messages_empty(db_session: AsyncDbSession, session: Session) -> None:
    """Test retrieving messages when session has no messages."""
    messages = await message_crud.get_messages(db_session, session.id)

    assert messages == []


async def test_create_message(db_session: AsyncDbSession, session: Session) -> None:
    """Test creating a single message."""
    msg = Message(kind=MessageKind.REQUEST, session_id=session.id, model_name="gpt-4")

    created = await message_crud.create_message(db_session, msg)

    assert created is not None
    assert created.id is not None
    assert created.kind == MessageKind.REQUEST
    assert created.session_id == session.id
    assert created.model_name == "gpt-4"


async def test_create_messages_batch(db_session: AsyncDbSession, session: Session) -> None:
    """Test creating multiple messages in batch."""
    messages = [
        Message(kind=MessageKind.REQUEST, session_id=session.id, model_name=None),
        Message(kind=MessageKind.RESPONSE, session_id=session.id, model_name=None),
        Message(kind=MessageKind.REQUEST, session_id=session.id, model_name=None),
    ]

    await message_crud.create_messages(db_session, messages)

    count = await message_crud.get_message_count(db_session, session.id)

    assert count == 3
