import enum
from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import Column, Enum
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from llm_gamebook.db.chat import Chat


class Sender(enum.StrEnum):
    HUMAN = "human"
    LLM = "llm"


class MessageBase(SQLModel):
    created_at: datetime = Field(default_factory=datetime.now)


class Message(MessageBase, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    sender: Sender = Field(sa_column=Column(Enum(Sender)))
    thinking: str | None
    text: str
    chat_id: UUID | None = Field(foreign_key="chat.id")
    chat: "Chat" = Relationship(back_populates="messages")
