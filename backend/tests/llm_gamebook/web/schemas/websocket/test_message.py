from datetime import UTC, datetime
from json import loads
from typing import TYPE_CHECKING
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
from llm_gamebook.story.state import ActionDispatched
from llm_gamebook.web.schemas.websocket.message import (
    WebSocketActionDispatchedMessage,
    WebSocketStreamMessageMessage,
    WebSocketStreamPartDeltaMessage,
    WebSocketStreamPartMessage,
)

if TYPE_CHECKING:
    from pydantic import JsonValue


def test_websocket_stream_message() -> None:
    session_id = uuid4()
    message = Message(
        id=uuid4(),
        session_id=session_id,
        kind=MessageKind.RESPONSE,
        finish_reason=None,
        parts=[Part(kind=PartKind.TEXT, content="Hello!")],
    )
    engine_msg = StreamMessageMessage(session_id=session_id, message=message)

    ws_msg = WebSocketStreamMessageMessage.from_message(engine_msg)

    assert ws_msg.kind == "stream_message"
    assert ws_msg.session_id == session_id
    assert ws_msg.message is not None


def test_websocket_stream_part() -> None:
    session_id = uuid4()
    message_id = uuid4()
    part = Part(id=uuid4(), message_id=message_id, kind=PartKind.TEXT, content="Hello!")
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


def test_websocket_action_dispatched_from_message() -> None:
    session_id = uuid4()
    action_type = "graph/transition"
    payload: JsonValue = {"entity_id": "locations", "to": "living_room"}
    timestamp = datetime.now(UTC)
    engine_msg = ActionDispatched(
        session_id=session_id,
        action_type=action_type,
        payload=payload,
        timestamp=timestamp,
    )

    ws_msg = WebSocketActionDispatchedMessage.from_message(engine_msg)

    assert ws_msg.kind == "action_dispatched"
    assert ws_msg.session_id == session_id
    assert ws_msg.action_type == action_type
    assert ws_msg.payload == payload
    assert ws_msg.timestamp == timestamp


def test_websocket_action_dispatched_serialization_camel_case() -> None:
    session_id = uuid4()
    timestamp = datetime.now(UTC)
    engine_msg = ActionDispatched(
        session_id=session_id,
        action_type="core/end-game",
        payload={"reason": "finished"},
        timestamp=timestamp,
    )

    ws_msg = WebSocketActionDispatchedMessage.from_message(engine_msg)
    data = loads(ws_msg.model_dump_json(by_alias=True))

    assert data["kind"] == "action_dispatched"
    assert data["sessionId"] == str(session_id)
    assert data["actionType"] == "core/end-game"
    assert data["payload"] == {"reason": "finished"}
    assert data["timestamp"] == timestamp.isoformat().replace("+00:00", "Z")
    assert "session_id" not in data
    assert "action_type" not in data


def test_part_kind_retry_prompt() -> None:
    assert PartKind.RETRY_PROMPT.value == "retry-prompt"
