from typing import TYPE_CHECKING, Annotated, Literal, Self
from uuid import UUID

from pydantic import BaseModel, Discriminator

from llm_gamebook.engine.message import Delta
from llm_gamebook.web.schemas.session.message import ModelMessage
from llm_gamebook.web.schemas.session.part import ModelResponsePart

if TYPE_CHECKING:
    from llm_gamebook.engine.message import (
        StreamMessageMessage,
        StreamPartDeltaMessage,
        StreamPartMessage,
    )


class BaseWebSocketMessage(BaseModel):
    kind: str


class BaseSessionWebSocketMessage(BaseModel):
    session_id: UUID


# --- Server messages ------------------------------------------------------------------------------


class WebSocketPongMessage(BaseWebSocketMessage):
    """An answer to a client ping."""

    kind: Literal["pong"] = "pong"


class WebSocketErrorMessage(BaseWebSocketMessage):
    """An error notification."""

    session_id: UUID | None = None
    kind: Literal["error"] = "error"
    name: str
    message: str

    @classmethod
    def from_exception(cls, session_id: UUID | None, exc: Exception) -> Self:
        return cls(session_id=session_id, name=type(exc).__name__, message=str(exc))


class WebSocketStreamStatusMessage(BaseSessionWebSocketMessage):
    """A status update."""

    kind: Literal["stream_status"] = "stream_status"
    status: Literal["started", "stopped"]


class WebSocketStreamMessageMessage(BaseSessionWebSocketMessage):
    """A streaming message update."""

    kind: Literal["stream_message"] = "stream_message"
    message: ModelMessage

    @classmethod
    def from_message(cls, msg: "StreamMessageMessage") -> Self:
        return cls.model_validate(msg, from_attributes=True)


class WebSocketStreamPartMessage(BaseSessionWebSocketMessage):
    """A streaming part update."""

    kind: Literal["stream_part"] = "stream_part"
    message_id: UUID
    part: ModelResponsePart

    @classmethod
    def from_message(cls, msg: "StreamPartMessage") -> Self:
        return cls.model_validate(msg, from_attributes=True)


class WebSocketStreamPartDeltaMessage(BaseSessionWebSocketMessage):
    """A streaming part delta update."""

    kind: Literal["stream_part_delta"] = "stream_part_delta"
    message_id: UUID
    part_id: UUID
    delta: Delta

    @classmethod
    def from_message(cls, msg: "StreamPartDeltaMessage") -> Self:
        return cls(
            session_id=msg.session_id,
            message_id=msg.message_id,
            part_id=msg.part_id,
            delta=msg.delta,
        )


type WebSocketServerMessage = Annotated[
    WebSocketPongMessage
    | WebSocketErrorMessage
    | WebSocketStreamStatusMessage
    | WebSocketStreamMessageMessage
    | WebSocketStreamPartMessage
    | WebSocketStreamPartDeltaMessage,
    Discriminator("kind"),
]
"""A WebSocket message sent from the backend."""

# --- Client messages ------------------------------------------------------------------------------


class WebSocketPingMessage(BaseWebSocketMessage):
    """A ping message."""

    kind: Literal["ping"] = "ping"


class WebSocketDummyMessage(BaseWebSocketMessage):
    kind: Literal["dummy"] = "dummy"


type WebSocketClientMessage = Annotated[
    WebSocketPingMessage | WebSocketDummyMessage,
    Discriminator("kind"),
]
"""A WebSocket message sent from the frontend."""
