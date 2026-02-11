from dataclasses import dataclass
from uuid import UUID

from pydantic_ai import ModelResponse

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
class ResponseStreamUpdateMessage(BaseMessage):
    session_id: UUID
    response: ModelResponse
    response_id: UUID
    part_ids: list[UUID]


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
