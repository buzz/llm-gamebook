from datetime import UTC, datetime
from uuid import uuid4

from llm_gamebook.db.models.message import FinishReason
from llm_gamebook.web.schema.session import (
    Session,
    SessionCreate,
    SessionFull,
    Sessions,
    SessionUpdate,
)
from llm_gamebook.web.schema.session.message import ModelRequest, ModelResponse, Usage
from llm_gamebook.web.schema.session.part import TextPart, UserPromptPart


def test_valid_session_create() -> None:
    config_id = uuid4()
    data = SessionCreate(config_id=config_id)
    assert data.config_id == config_id
    assert data.title is None


def test_valid_session_create_with_title() -> None:
    config_id = uuid4()
    title = "My Session"
    data = SessionCreate(config_id=config_id, title=title)
    assert data.config_id == config_id
    assert data.title == title


def test_valid_session_update_with_title() -> None:
    data = SessionUpdate(title="Updated Title")
    assert data.title == "Updated Title"
    assert data.config_id is None


def test_valid_session_update_with_config_id() -> None:
    config_id = uuid4()
    data = SessionUpdate(config_id=config_id)
    assert data.config_id == config_id
    assert data.title is None


def test_valid_session_update_full() -> None:
    config_id = uuid4()
    title = "Updated Session"
    data = SessionUpdate(config_id=config_id, title=title)
    assert data.config_id == config_id
    assert data.title == title


def test_empty_session_update_is_valid() -> None:
    data = SessionUpdate()
    assert data.title is None
    assert data.config_id is None


def test_session_full_with_messages() -> None:
    session_id = uuid4()
    config_id = uuid4()

    message_id = uuid4()
    part_id = uuid4()

    user_prompt = UserPromptPart(
        id=part_id,
        content="Hello",
        timestamp=datetime.now(UTC),
    )
    model_request = ModelRequest(
        id=message_id,
        parts=[user_prompt],
        instructions=None,
    )

    session = SessionFull(
        id=session_id,
        config_id=config_id,
        title="Test",
        messages=[model_request],
    )
    assert session.messages == [model_request]
    assert len(session.messages) == 1


def test_session_full_with_empty_messages() -> None:
    session_id = uuid4()
    config_id = uuid4()

    session = SessionFull(
        id=session_id,
        config_id=config_id,
        title="Test",
        messages=[],
    )
    assert session.messages == []
    assert len(session.messages) == 0


def test_session_full_with_request_and_response() -> None:
    session_id = uuid4()
    config_id = uuid4()
    timestamp = datetime.now(UTC)

    request_id = uuid4()
    response_id = uuid4()
    part_id1 = uuid4()
    part_id2 = uuid4()

    user_prompt = UserPromptPart(
        id=part_id1,
        content="What is 2+2?",
        timestamp=timestamp,
    )
    request = ModelRequest(
        id=request_id,
        parts=[user_prompt],
        instructions=None,
    )

    text_part = TextPart(
        id=part_id2,
        content="2+2 equals 4",
    )
    usage = Usage(
        input_tokens=10,
        output_tokens=20,
        cache_write_tokens=0,
        cache_read_tokens=0,
    )
    response = ModelResponse(
        id=response_id,
        parts=[text_part],
        usage=usage,
        model_name="gpt-4",
        timestamp=timestamp,
        provider_name="openai",
        finish_reason=FinishReason.STOP,
    )

    session = SessionFull(
        id=session_id,
        config_id=config_id,
        title="Math Session",
        messages=[request, response],
    )
    assert len(session.messages) == 2


def test_session_full_message_discriminator() -> None:
    session_id = uuid4()
    config_id = uuid4()
    timestamp = datetime.now(UTC)

    request_id = uuid4()
    response_id = uuid4()

    user_prompt = UserPromptPart(
        id=uuid4(),
        content="Test",
        timestamp=timestamp,
    )
    request = ModelRequest(
        id=request_id,
        parts=[user_prompt],
        instructions=None,
    )

    text_part = TextPart(
        id=uuid4(),
        content="Response",
    )
    response = ModelResponse(
        id=response_id,
        parts=[text_part],
        usage=Usage(
            input_tokens=1,
            output_tokens=1,
            cache_write_tokens=0,
            cache_read_tokens=0,
        ),
        timestamp=timestamp,
    )

    session = SessionFull(
        id=session_id,
        config_id=config_id,
        messages=[request, response],
    )

    messages = session.messages
    assert messages[0].kind == "request"
    assert messages[1].kind == "response"


def test_sessions_empty_list() -> None:
    sessions = Sessions(data=[], count=0)
    assert sessions.data == []
    assert sessions.count == 0


def test_sessions_with_single_session() -> None:
    session_id = uuid4()
    config_id = uuid4()

    session = Session(
        id=session_id,
        config_id=config_id,
        title="Test Session",
    )

    sessions = Sessions(data=[session], count=1)
    assert len(sessions.data) == 1
    assert sessions.count == 1
    assert sessions.data[0].id == session_id


def test_sessions_with_multiple_sessions() -> None:
    sessions_list = [
        Session(
            id=uuid4(),
            config_id=uuid4(),
            title=f"Session {i}",
        )
        for i in range(3)
    ]

    sessions = Sessions(data=sessions_list, count=3)
    assert len(sessions.data) == 3
    assert sessions.count == 3


def test_sessions_count_matches_data_length() -> None:
    sessions_list = [
        Session(
            id=uuid4(),
            config_id=uuid4(),
            title=f"Session {i}",
        )
        for i in range(5)
    ]

    sessions = Sessions(data=sessions_list, count=len(sessions_list))
    assert sessions.count == len(sessions.data)


def test_sessions_with_no_title() -> None:
    session = Session(
        id=uuid4(),
        config_id=uuid4(),
    )

    sessions = Sessions(data=[session], count=1)
    assert sessions.data[0].title is None
