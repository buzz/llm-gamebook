from datetime import UTC, datetime
from typing import TYPE_CHECKING
from uuid import uuid4

import pytest

from llm_gamebook.story.state import ActionDispatched
from llm_gamebook.story.state.messages import ActionDispatched as ActionDispatchedDirect

if TYPE_CHECKING:
    from pydantic import JsonValue


def test_action_dispatched_field_roundtrip() -> None:
    session_id = uuid4()
    timestamp = datetime.now(UTC)
    payload: JsonValue = {"reason": "completed"}

    message = ActionDispatched(
        session_id=session_id,
        action_type="core/end-game",
        payload=payload,
        timestamp=timestamp,
    )

    assert message.session_id == session_id
    assert message.action_type == "core/end-game"
    assert message.payload == payload
    assert message.timestamp == timestamp


def test_action_dispatched_is_frozen() -> None:
    message = ActionDispatched(
        session_id=uuid4(),
        action_type="core/end-game",
        payload={},
        timestamp=datetime.now(UTC),
    )

    with pytest.raises(AttributeError):
        message.session_id = uuid4()  # type: ignore[misc]


def test_action_dispatched_importable_from_state_module() -> None:
    assert ActionDispatched is ActionDispatchedDirect


def test_action_dispatched_payload_accepts_json_values() -> None:
    payload: JsonValue = {"count": 1, "active": True, "score": 1.5, "items": [1, 2, 3]}
    message = ActionDispatched(
        session_id=uuid4(),
        action_type="graph/transition",
        payload=payload,
        timestamp=datetime.now(UTC),
    )

    assert message.payload == payload
