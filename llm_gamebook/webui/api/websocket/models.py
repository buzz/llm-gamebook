from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel


class BaseMessage(BaseModel):
    event: str
    id: UUID
    created_at: datetime


class ServerLLMMessage(BaseMessage):
    event: Literal["llm_message"] = "llm_message"
    thinking: str | None
    text: str | None
