from dataclasses import FrozenInstanceError
from uuid import uuid4

import pytest
from pydantic_ai import ModelResponse, RequestUsage, TextPart

from llm_gamebook.engine.message import (
    EngineCreated,
    ResponseErrorMessage,
    ResponseStartedMessage,
    ResponseStoppedMessage,
    ResponseStreamUpdateMessage,
    ResponseUserRequestMessage,
    SessionDeleted,
    SessionModelConfigChangedMessage,
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


def test_response_stream_update_message() -> None:
    """Test ResponseStreamUpdateMessage construction."""
    session_id = uuid4()
    response_id = uuid4()
    part_ids = [uuid4(), uuid4()]
    response = ModelResponse(
        parts=[TextPart(content="Hello")],
        model_name="gpt-4",
        usage=RequestUsage(input_tokens=5, output_tokens=3),
    )
    msg = ResponseStreamUpdateMessage(
        session_id=session_id,
        response=response,
        response_id=response_id,
        part_ids=part_ids,
    )

    assert isinstance(msg, BaseMessage)
    assert msg.session_id == session_id
    assert msg.response == response
    assert msg.response_id == response_id
    assert msg.part_ids == part_ids


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
