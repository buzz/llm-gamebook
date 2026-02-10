from dataclasses import dataclass
from uuid import UUID

from pydantic_ai import ModelResponse

from llm_gamebook.providers import ModelProvider


@dataclass
class StreamUpdateBusMessage:
    session_id: UUID
    response: ModelResponse
    response_id: UUID
    part_ids: list[UUID]


@dataclass
class ResponseErrorBusMessage:
    session_id: UUID
    error: Exception


@dataclass
class ModelConfigChangedMessage:
    session_id: UUID
    model_name: str
    provider: ModelProvider
    base_url: str | None
    api_key: str | None
