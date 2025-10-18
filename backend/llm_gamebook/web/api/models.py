from datetime import datetime
from uuid import UUID

from sqlmodel import SQLModel

from llm_gamebook.db.chat import ChatBase
from llm_gamebook.db.message import MessageBase, Sender


class ServerMessage(SQLModel):
    message: str


class ChatCreate(ChatBase):
    pass


class ChatPublic(ChatBase):
    id: UUID
    created_at: datetime
    messages: "list[MessageListPublic]"


class ChatListPublic(ChatBase):
    id: UUID
    created_at: datetime


class ChatsPublic(SQLModel):
    data: list[ChatListPublic]
    count: int


class MessageListPublic(MessageBase):
    id: UUID
    created_at: datetime
    sender: Sender
    thinking: str | None
    text: str
