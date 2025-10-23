import json
from functools import singledispatch
from typing import TYPE_CHECKING, Annotated, Any, Literal, Self, TypeAliasType
from uuid import UUID

import pydantic_ai
from pydantic import BaseModel, Discriminator, TypeAdapter

from llm_gamebook.web.api.models import (
    ModelResponse,
    ModelResponsePart,
    TextPart,
    ThinkingPart,
    ToolCallPart,
)

if TYPE_CHECKING:
    from llm_gamebook.engine.engine import StreamUpdateBusMessage


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
    def from_stream_update(cls, msg: "StreamUpdateBusMessage") -> Self:
        api_response = ModelResponse.model_validate({
            "id": msg["response_id"],
            "parts": [
                convert_part(part, msg["part_ids"][idx])
                for idx, part in enumerate(msg["response"].parts)
            ],
            "usage": msg["response"].usage,
            "model_name": msg["response"].model_name,
            "timestamp": msg["response"].timestamp,
            "provider_name": msg["response"].provider_name,
            "finish_reason": msg["response"].finish_reason,
        })
        return cls(session_id=msg["session_id"], response=api_response)


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

# --- OpenAPI schema patching ----------------------------------------------------------------------


def _fix_refs(obj: list | dict[str, Any]) -> None:
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, str) and v.startswith("#/$defs/"):
                obj[k] = f"#/components/schemas/{v.split('#/$defs/')[1]}"
            else:
                _fix_refs(v)
    elif isinstance(obj, list):
        for v in obj:
            _fix_refs(v)


def _get_schema(type_alias: TypeAliasType, components: dict[str, Any]) -> dict[str, Any]:
    schema = TypeAdapter(type_alias).json_schema()

    # Extract and merge defs at top level
    defs = schema.pop("$defs", {})
    components.update(defs)

    return schema


def add_websocket_schema(schema: dict[str, Any]) -> None:
    components = schema["components"]["schemas"]

    server_msg_schema = _get_schema(WebSocketServerMessage, components)
    components[WebSocketServerMessage.__name__] = server_msg_schema

    client_msg_schema = _get_schema(WebSocketClientMessage, components)
    components[WebSocketClientMessage.__name__] = client_msg_schema

    schema["info"]["x-websockets"] = [
        {
            "name": "Session",
            "path": "/api/ws/{session_id}",
            "messages": {
                "send": {"$ref": f"#/components/schemas/{WebSocketServerMessage.__name__}"},
                "receive": {"$ref": f"#/components/schemas/{WebSocketClientMessage.__name__}"},
            },
        },
    ]

    _fix_refs(schema)


# --- Conversion registry --------------------------------------------------------------------------


@singledispatch
def convert_part(part: Any, part_id: UUID) -> ModelResponsePart:
    msg = f"Unknown part type: {type(part)}"
    raise TypeError(msg)


@convert_part.register
def _(part: pydantic_ai.TextPart, part_id: UUID) -> ModelResponsePart:
    return TextPart(id=part_id, content=part.content)


@convert_part.register
def _(part: pydantic_ai.ToolCallPart, part_id: UUID) -> ModelResponsePart:
    args = json.dumps(part.args) if isinstance(part.args, (dict, list)) else part.args
    return ToolCallPart(
        id=part_id,
        args=args,
        tool_name=part.tool_name,
        tool_call_id=part.tool_call_id,
    )


@convert_part.register
def _(part: pydantic_ai.ThinkingPart, part_id: UUID) -> ModelResponsePart:
    return ThinkingPart(
        id=part_id,
        content=part.content,
        provider_name=part.provider_name,
    )
