from datetime import datetime
from uuid import UUID, uuid4

from sqlmodel import Field, Relationship, SQLModel

from llm_gamebook.db.message import Message


class ChatBase(SQLModel):
    created_at: datetime = Field(default_factory=datetime.now)


class Chat(ChatBase, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    messages: list[Message] = Relationship(
        back_populates="chat", sa_relationship_kwargs={"lazy": "selectin"}
    )
