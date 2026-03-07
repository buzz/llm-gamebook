from dataclasses import FrozenInstanceError
from uuid import uuid4

import pytest

from llm_gamebook.db.models import Message, Part
from llm_gamebook.db.models.message import MessageKind
from llm_gamebook.db.models.part import PartKind
from llm_gamebook.engine.message import (
    ContentDelta,
    EngineCreated,
    ResponseErrorMessage,
    ResponseStartedMessage,
    ResponseStoppedMessage,
    ResponseUserRequestMessage,
    SessionDeleted,
    SessionModelConfigChangedMessage,
    StreamMessageMessage,
    StreamPartDeltaMessage,
    StreamPartMessage,
    ToolArgsDelta,
    ToolNameDelta,
)
from llm_gamebook.message_bus.messages import BaseMessage
from llm_gamebook.providers import ModelProvider


def test_engine_created_message() -> None:
    """Test EngineCreated message construction."""
    session_id = uuid4()
    msg = EngineCreated(session_id=session_id)

    assert isinstance(msg, BaseMessage)
    assert msg.session_id == session_id


def test_session_deleted_message() -> None:
    """Test SessionDeleted message construction."""
    session_id = uuid4()
    msg = SessionDeleted(session_id=session_id)

    assert isinstance(msg, BaseMessage)
    assert msg.session_id == session_id


def test_response_user_request_message() -> None:
    """Test ResponseUserRequestMessage construction."""
    session_id = uuid4()
    msg = ResponseUserRequestMessage(session_id=session_id)

    assert isinstance(msg, BaseMessage)
    assert msg.session_id == session_id


def test_response_started_message() -> None:
    """Test ResponseStartedMessage construction."""
    session_id = uuid4()
    msg = ResponseStartedMessage(session_id=session_id)

    assert isinstance(msg, BaseMessage)
    assert msg.session_id == session_id


def test_response_stopped_message() -> None:
    """Test ResponseStoppedMessage construction."""
    session_id = uuid4()
    msg = ResponseStoppedMessage(session_id=session_id)

    assert isinstance(msg, BaseMessage)
    assert msg.session_id == session_id


def test_stream_message_message() -> None:
    """Test StreamMessageMessage construction."""
    session_id = uuid4()
    msg = StreamMessageMessage(
        session_id=session_id,
        message=Message(
            id=uuid4(),
            session_id=session_id,
            kind=MessageKind.RESPONSE,
            finish_reason=None,
        ),
    )

    assert isinstance(msg, BaseMessage)
    assert msg.session_id == session_id
    assert msg.message.id is not None


def test_stream_part_message() -> None:
    """Test StreamPartMessage construction."""
    session_id = uuid4()
    message_id = uuid4()
    msg = StreamPartMessage(
        session_id=session_id,
        message_id=message_id,
        part=Part(
            id=uuid4(),
            message_id=message_id,
            kind=PartKind.TEXT,
            content="Hello",
            tool_name=None,
            tool_call_id=None,
            args=None,
        ),
    )

    assert isinstance(msg, BaseMessage)
    assert msg.session_id == session_id
    assert msg.message_id == message_id
    assert msg.part.id is not None


def test_stream_part_delta_message() -> None:
    """Test StreamPartDeltaMessage construction."""
    session_id = uuid4()
    message_id = uuid4()
    part_id = uuid4()
    delta = ContentDelta(content="Hello world")
    msg = StreamPartDeltaMessage(
        session_id=session_id,
        message_id=message_id,
        part_id=part_id,
        delta=delta,
    )

    assert isinstance(msg, BaseMessage)
    assert msg.session_id == session_id
    assert msg.message_id == message_id
    assert msg.part_id == part_id
    content_delta: ContentDelta = msg.delta  # type: ignore[assignment]
    assert content_delta.content == "Hello world"


def test_content_delta() -> None:
    """Test ContentDelta creation."""
    delta = ContentDelta(content="Hello")
    assert delta.content == "Hello"
    assert delta.kind == "content"


def test_tool_args_delta() -> None:
    """Test ToolArgsDelta creation."""
    delta = ToolArgsDelta(args='{"key": "value"}')
    assert delta.args == '{"key": "value"}'
    assert delta.kind == "tool_args"


def test_tool_name_delta() -> None:
    """Test ToolNameDelta creation."""
    delta = ToolNameDelta(tool_name="search")
    assert delta.tool_name == "search"
    assert delta.kind == "tool_name"


def test_delta_discriminator() -> None:
    """Test that Delta discriminator works correctly."""
    content = ContentDelta(content="test")
    tool_args = ToolArgsDelta(args="args")
    tool_name = ToolNameDelta(tool_name="test")

    assert content.kind == "content"
    assert tool_args.kind == "tool_args"
    assert tool_name.kind == "tool_name"


def test_new_messages_are_immutable() -> None:
    """Test immutability of new message types."""
    session_id = uuid4()

    msg1 = StreamMessageMessage(
        session_id=session_id,
        message=Message(
            id=uuid4(),
            session_id=session_id,
            kind=MessageKind.RESPONSE,
            finish_reason=None,
        ),
    )
    with pytest.raises(FrozenInstanceError):
        msg1.session_id = uuid4()  # type: ignore[misc]

    msg2 = StreamPartMessage(
        session_id=session_id,
        message_id=uuid4(),
        part=Part(
            id=uuid4(),
            message_id=uuid4(),
            kind=PartKind.TEXT,
            content="test",
            tool_name=None,
            tool_call_id=None,
            args=None,
        ),
    )
    with pytest.raises(FrozenInstanceError):
        msg2.session_id = uuid4()  # type: ignore[misc]

    msg3 = StreamPartDeltaMessage(
        session_id=session_id,
        message_id=uuid4(),
        part_id=uuid4(),
        delta=ContentDelta(content="test"),
    )
    with pytest.raises(FrozenInstanceError):
        msg3.session_id = uuid4()  # type: ignore[misc]

    delta1 = ContentDelta(content="test")
    with pytest.raises(FrozenInstanceError):
        delta1.content = "new"  # type: ignore[misc]

    delta2 = ToolArgsDelta(args="test")
    with pytest.raises(FrozenInstanceError):
        delta2.args = "new"  # type: ignore[misc]

    delta3 = ToolNameDelta(tool_name="test")
    with pytest.raises(FrozenInstanceError):
        delta3.tool_name = "new"  # type: ignore[misc]


def test_response_error_message() -> None:
    """Test ResponseErrorMessage construction."""
    session_id = uuid4()
    error = ValueError("Test error")
    msg = ResponseErrorMessage(session_id=session_id, error=error)

    assert isinstance(msg, BaseMessage)
    assert msg.session_id == session_id
    assert msg.error is error
    assert str(msg.error) == "Test error"


def test_session_model_config_changed_message() -> None:
    """Test SessionModelConfigChangedMessage construction."""
    session_id = uuid4()
    model_name = "gpt-4"
    provider = ModelProvider.OPENAI
    base_url = "https://api.openai.com/v1"
    api_key = "sk-test-key"

    msg = SessionModelConfigChangedMessage(
        session_id=session_id,
        model_name=model_name,
        provider=provider,
        base_url=base_url,
        api_key=api_key,
    )

    assert isinstance(msg, BaseMessage)
    assert msg.session_id == session_id
    assert msg.model_name == model_name
    assert msg.provider == provider
    assert msg.base_url == base_url
    assert msg.api_key == api_key


def test_session_model_config_changed_message_optional_fields() -> None:
    """Test SessionModelConfigChangedMessage with optional fields as None."""
    session_id = uuid4()
    msg = SessionModelConfigChangedMessage(
        session_id=session_id,
        model_name="gpt-4",
        provider=ModelProvider.OLLAMA,
        base_url=None,
        api_key=None,
    )

    assert msg.base_url is None
    assert msg.api_key is None


def test_messages_are_frozen() -> None:
    """Test that messages are immutable (frozen dataclasses)."""
    session_id = uuid4()
    msg = EngineCreated(session_id=session_id)

    with pytest.raises(FrozenInstanceError):
        msg.session_id = uuid4()  # type: ignore[misc]
