from typing import Literal
from uuid import UUID

from pydantic import BaseModel

from llm_gamebook.db.message import MessageBase


class MessageRead(MessageBase):
    id: UUID
    thinking: str | None
    text: str


class MessageUpdate(BaseModel):
    event: Literal["llm_message"] = "llm_message"
    finish_reason: Literal["stop"] | None = None
    message: MessageRead
