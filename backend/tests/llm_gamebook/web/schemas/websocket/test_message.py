from datetime import UTC, datetime
from uuid import uuid4

from llm_gamebook.db.models import Message, Part
from llm_gamebook.db.models.message import MessageKind
from llm_gamebook.db.models.part import PartKind
from llm_gamebook.engine.message import (
    ContentDelta,
    StreamMessageMessage,
    StreamPartDeltaMessage,
    StreamPartMessage,
)
from llm_gamebook.web.schemas.websocket.message import (
    WebSocketStreamMessageMessage,
    WebSocketStreamPartDeltaMessage,
    WebSocketStreamPartMessage,
)


def test_websocket_stream_message() -> None:
    session_id = uuid4()
    message = Message(
        id=uuid4(),
        session_id=session_id,
        kind=MessageKind.RESPONSE,
        finish_reason=None,
        parts=[
            Part(
                kind=PartKind.TEXT,
                content="Hello!",
                timestamp=datetime.now(UTC),
                tool_name=None,
                tool_call_id=None,
                args=None,
            )
        ],
    )
    engine_msg = StreamMessageMessage(session_id=session_id, message=message)

    ws_msg = WebSocketStreamMessageMessage.from_message(engine_msg)

    assert ws_msg.kind == "stream_message"
    assert ws_msg.session_id == session_id
    assert ws_msg.message is not None


def test_websocket_stream_part() -> None:
    session_id = uuid4()
    message_id = uuid4()
    part = Part(
        id=uuid4(),
        message_id=message_id,
        kind=PartKind.TEXT,
        content="Hello!",
        timestamp=datetime.now(UTC),
        tool_name=None,
        tool_call_id=None,
        args=None,
    )
    engine_msg = StreamPartMessage(
        session_id=session_id,
        message_id=message_id,
        part=part,
    )

    ws_msg = WebSocketStreamPartMessage.from_message(engine_msg)

    assert ws_msg.kind == "stream_part"
    assert ws_msg.session_id == session_id
    assert ws_msg.message_id == message_id


def test_websocket_stream_part_delta() -> None:
    session_id = uuid4()
    message_id = uuid4()
    part_id = uuid4()
    delta = ContentDelta(content="Hello world!")
    engine_msg = StreamPartDeltaMessage(
        session_id=session_id,
        message_id=message_id,
        part_id=part_id,
        delta=delta,
    )

    ws_msg = WebSocketStreamPartDeltaMessage.from_message(engine_msg)

    assert ws_msg.kind == "stream_part_delta"
    assert ws_msg.session_id == session_id
    assert ws_msg.message_id == message_id
    assert ws_msg.part_id == part_id


def test_part_kind_retry_prompt() -> None:
    assert PartKind.RETRY_PROMPT.value == "retry-prompt"
