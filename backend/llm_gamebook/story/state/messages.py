from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from pydantic import JsonValue

from llm_gamebook.message_bus import BaseMessage


@dataclass(frozen=True)
class ActionDispatched(BaseMessage):
    """Message published to the application message bus when a story action is dispatched."""

    session_id: UUID
    action_type: str
    payload: JsonValue
    timestamp: datetime
