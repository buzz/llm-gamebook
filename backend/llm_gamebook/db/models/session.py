from datetime import datetime
from uuid import UUID, uuid4

from sqlmodel import Field, Relationship, SQLModel

from .message import Message


class SessionBase(SQLModel):
    timestamp: datetime = Field(default_factory=datetime.now)


class Session(SessionBase, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    title: str | None
    messages: list[Message] = Relationship(
        back_populates="session",
        passive_deletes="all",
        # Without this, we get MissingGreenlet errors on lazy attribute access
        # https://docs.sqlalchemy.org/en/20/errors.html#missinggreenlet
        sa_relationship_kwargs={"lazy": "selectin"},
    )
