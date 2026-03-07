from dataclasses import dataclass
from typing import Annotated, Literal
from uuid import UUID

from pydantic import Discriminator

from llm_gamebook.db.models import Message, Part
from llm_gamebook.message_bus import BaseMessage
from llm_gamebook.providers import ModelProvider


@dataclass(frozen=True)
class EngineCreated(BaseMessage):
    session_id: UUID


@dataclass(frozen=True)
class SessionDeleted(BaseMessage):
    session_id: UUID


@dataclass(frozen=True)
class ResponseUserRequestMessage(BaseMessage):
    session_id: UUID


@dataclass(frozen=True)
class ResponseStartedMessage(BaseMessage):
    session_id: UUID


@dataclass(frozen=True)
class ResponseStoppedMessage(BaseMessage):
    session_id: UUID


@dataclass(frozen=True)
class StreamMessageMessage(BaseMessage):
    session_id: UUID
    message: Message


@dataclass(frozen=True)
class StreamPartMessage(BaseMessage):
    session_id: UUID
    message_id: UUID
    part: Part


@dataclass(frozen=True)
class ContentDelta:
    content: str
    kind: Literal["content"] = "content"


@dataclass(frozen=True)
class ToolArgsDelta:
    args: str
    kind: Literal["tool_args"] = "tool_args"


@dataclass(frozen=True)
class ToolNameDelta:
    tool_name: str
    kind: Literal["tool_name"] = "tool_name"


type Delta = Annotated[ContentDelta | ToolArgsDelta | ToolNameDelta, Discriminator("kind")]


@dataclass(frozen=True)
class StreamPartDeltaMessage(BaseMessage):
    session_id: UUID
    message_id: UUID
    part_id: UUID
    delta: Delta


@dataclass(frozen=True)
class ResponseErrorMessage(BaseMessage):
    session_id: UUID
    error: Exception


@dataclass(frozen=True)
class SessionModelConfigChangedMessage(BaseMessage):
    session_id: UUID
    model_name: str
    provider: ModelProvider
    base_url: str | None
    api_key: str | None
