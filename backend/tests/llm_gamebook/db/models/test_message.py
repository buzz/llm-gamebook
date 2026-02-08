from datetime import UTC, datetime
from uuid import uuid4

from pydantic_ai import ModelRequest, ModelResponse
from pydantic_ai.messages import SystemPromptPart, TextPart, UserPromptPart
from sqlmodel.ext.asyncio.session import AsyncSession as AsyncDbSession

from llm_gamebook.db.crud import message as message_crud
from llm_gamebook.db.models import Message, Session
from llm_gamebook.db.models.message import FinishReason, MessageKind
from llm_gamebook.db.models.part import Part, PartKind


async def test_get_message_count(db_session: AsyncDbSession, session: Session) -> None:
    initial_count = await message_crud.get_message_count(db_session, session.id)

    message = Message(
        session_id=session.id,
        kind=MessageKind.REQUEST,
        model_name=None,
        finish_reason=None,
        parts=[
            Part(
                part_kind=PartKind.USER_PROMPT,
                content="Hello",
                timestamp=datetime.now(UTC),
                tool_name=None,
                tool_call_id=None,
                args=None,
            )
        ],
    )
    await message_crud.create_message(db_session, message)

    new_count = await message_crud.get_message_count(db_session, session.id)

    assert new_count == initial_count + 1


async def test_get_messages_empty(db_session: AsyncDbSession, session: Session) -> None:
    messages = await message_crud.get_messages(db_session, session.id)

    assert messages == []


async def test_get_messages_with_data(db_session: AsyncDbSession, session: Session) -> None:
    msg1 = Message(
        session_id=session.id,
        kind=MessageKind.REQUEST,
        model_name=None,
        finish_reason=None,
        parts=[
            Part(
                part_kind=PartKind.USER_PROMPT,
                content="Hello 1",
                timestamp=datetime.now(UTC),
                tool_name=None,
                tool_call_id=None,
                args=None,
            )
        ],
    )
    msg2 = Message(
        session_id=session.id,
        kind=MessageKind.RESPONSE,
        model_name="gpt-4",
        finish_reason=FinishReason.STOP,
        parts=[
            Part(
                part_kind=PartKind.TEXT,
                content="Hi there!",
                timestamp=datetime.now(UTC),
                tool_name=None,
                tool_call_id=None,
                args=None,
            )
        ],
    )
    await message_crud.create_message(db_session, msg1)
    await message_crud.create_message(db_session, msg2)

    messages = await message_crud.get_messages(db_session, session.id)

    assert len(messages) == 2


async def test_create_message(db_session: AsyncDbSession, session: Session) -> None:
    message = Message(
        session_id=session.id,
        kind=MessageKind.REQUEST,
        model_name=None,
        finish_reason=None,
        parts=[
            Part(
                part_kind=PartKind.USER_PROMPT,
                content="Test message",
                timestamp=datetime.now(UTC),
                tool_name=None,
                tool_call_id=None,
                args=None,
            )
        ],
    )
    created = await message_crud.create_message(db_session, message)

    assert created.id is not None
    assert created.session_id == session.id
    assert created.kind == MessageKind.REQUEST


async def test_create_messages_batch(db_session: AsyncDbSession, session: Session) -> None:
    messages = [
        Message(
            session_id=session.id,
            kind=MessageKind.REQUEST,
            model_name=None,
            finish_reason=None,
            parts=[
                Part(
                    part_kind=PartKind.USER_PROMPT,
                    content=f"Message {i}",
                    timestamp=datetime.now(UTC),
                    tool_name=None,
                    tool_call_id=None,
                    args=None,
                )
            ],
        )
        for i in range(3)
    ]
    await message_crud.create_messages(db_session, messages)

    count = await message_crud.get_message_count(db_session, session.id)

    assert count == 3


def test_message_from_model_message_request() -> None:
    session_id = uuid4()
    msg_id = uuid4()

    model_request = ModelRequest([
        SystemPromptPart(content="You are a helpful assistant"),
        UserPromptPart(content="Hello, world!"),
    ])

    message = Message.from_model_message(model_request, session_id, msg_id, None)

    assert message.id == msg_id
    assert message.session_id == session_id
    assert message.kind == MessageKind.REQUEST
    assert message.model_name is None
    assert len(message.parts) == 2


def test_message_from_model_message_response() -> None:
    session_id = uuid4()
    msg_id = uuid4()
    part_ids = [uuid4(), uuid4()]

    model_response = ModelResponse(
        model_name="gpt-4",
        finish_reason="stop",
        timestamp=datetime.now(UTC),
        parts=[TextPart(content="Hello!"), TextPart(content="How can I help?")],
    )

    message = Message.from_model_message(model_response, session_id, msg_id, part_ids)

    assert message.id == msg_id
    assert message.session_id == session_id
    assert message.kind == MessageKind.RESPONSE
    assert message.model_name == "gpt-4"
    assert message.finish_reason == FinishReason.STOP
    assert len(message.parts) == 2


def test_message_to_dict() -> None:
    session_id = uuid4()
    message_id = uuid4()
    timestamp = datetime.now(UTC)

    message = Message(
        id=message_id,
        session_id=session_id,
        timestamp=timestamp,
        kind=MessageKind.RESPONSE,
        model_name="gpt-4",
        finish_reason=FinishReason.STOP,
        parts=[
            Part(
                part_kind=PartKind.TEXT,
                content="Hello!",
                timestamp=timestamp,
                tool_name=None,
                tool_call_id=None,
                args=None,
            )
        ],
    )

    result = message.to_dict()

    # type checking disabled because to_dict() returns Mapping[str, object]
    assert result["id"] == str(message_id)
    assert result["session_id"] == str(session_id)
    assert isinstance(result["timestamp"], str)
    assert result["kind"] == "response"
    assert result["model_name"] == "gpt-4"
    assert result["finish_reason"] == "stop"
    assert len(result["parts"]) == 1  # type: ignore[arg-type]
    assert result["parts"][0]["content"] == "Hello!"  # type: ignore[index]
