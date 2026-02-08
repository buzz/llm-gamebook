from datetime import datetime
from uuid import UUID, uuid4

from sqlmodel import Field, Relationship, SQLModel

from .message import Message
from .model_config import ModelConfig


class SessionBase(SQLModel):
    timestamp: datetime = Field(default_factory=datetime.now)


class Session(SessionBase, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    title: str | None
    config: ModelConfig | None = Relationship(back_populates="sessions")
    config_id: UUID | None = Field(default=None, foreign_key="modelconfig.id")
    messages: list[Message] = Relationship(
        back_populates="session",
        passive_deletes="all",
        sa_relationship_kwargs={"lazy": "selectin"},
    )
