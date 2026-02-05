from dataclasses import dataclass
from uuid import UUID

from pydantic_ai import ModelResponse


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
