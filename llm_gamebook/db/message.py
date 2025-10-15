import enum
import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Column, Enum
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from llm_gamebook.db.chat import Chat


class Sender(enum.Enum):
    HUMAN = enum.auto()
    LLM = enum.auto()


class Message(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    sender: Sender = Field(sa_column=Column(Enum(Sender)))
    content: str
    chat_id: int | None = Field(default=None, foreign_key="chat.id")
    chat: "Chat" = Relationship(back_populates="messages")
