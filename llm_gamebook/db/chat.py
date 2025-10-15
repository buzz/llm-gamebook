import uuid
from datetime import datetime

from sqlmodel import Field, Relationship, SQLModel

from llm_gamebook.db.message import Message


class ChatBase(SQLModel):
    created_at: datetime = Field(default_factory=datetime.now)


class Chat(ChatBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    messages: list[Message] = Relationship(back_populates="chat")


class ChatCreate(ChatBase):
    pass


class ChatPublic(ChatBase):
    id: uuid.UUID
    messages: list[Message]


class ChatListPublic(ChatBase):
    id: uuid.UUID


class ChatsPublic(SQLModel):
    data: list[ChatListPublic]
    count: int
