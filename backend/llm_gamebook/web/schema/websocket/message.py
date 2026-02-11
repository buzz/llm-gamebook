from typing import TYPE_CHECKING, Annotated, Literal, Self
from uuid import UUID

from pydantic import BaseModel, Discriminator

from llm_gamebook.web.schema.session.message import ModelResponse

from ._convert_part import convert_part

if TYPE_CHECKING:
    from llm_gamebook.engine.message import ResponseStreamUpdateMessage


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


class WebSocketStatusMessage(BaseSessionWebSocketMessage):
    """A status update."""

    kind: Literal["status"] = "status"
    status: Literal["started", "stopped"]


class WebSocketStreamMessage(BaseSessionWebSocketMessage):
    """A streaming update."""

    kind: Literal["stream"] = "stream"
    response: ModelResponse

    @classmethod
    def from_stream_update(cls, msg: "ResponseStreamUpdateMessage") -> Self:
        api_response = ModelResponse.model_validate({
            "id": msg.response_id,
            "parts": [
                convert_part(part, msg.part_ids[idx]) for idx, part in enumerate(msg.response.parts)
            ],
            "usage": msg.response.usage,
            "model_name": msg.response.model_name,
            "timestamp": msg.response.timestamp,
            "provider_name": msg.response.provider_name,
            "finish_reason": msg.response.finish_reason,
        })
        return cls(session_id=msg.session_id, response=api_response)


type WebSocketServerMessage = Annotated[
    WebSocketPongMessage | WebSocketErrorMessage | WebSocketStatusMessage | WebSocketStreamMessage,
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
