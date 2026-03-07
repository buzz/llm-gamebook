import enum
from collections.abc import Mapping
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Optional, Self
from uuid import UUID, uuid4

from pydantic_ai import ModelRequest, ModelResponse
from sqlalchemy import JSON, Column, Enum, String
from sqlmodel import Field, Relationship, SQLModel

from .part import Part
from .usage import Usage

if TYPE_CHECKING:
    from .session import Session


class MessageKind(enum.StrEnum):
    REQUEST = "request"
    RESPONSE = "response"


class FinishReason(enum.StrEnum):
    STOP = "stop"
    LENGTH = "length"
    CONTENT_LENGTH = "content_length"
    TOOL_CALL = "tool_call"
    ERROR = "error"


class MessageBase(SQLModel):
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    kind: MessageKind = Field(sa_column=Column(Enum(MessageKind)))
    finish_reason: FinishReason | None = Field(sa_column=Column(Enum(FinishReason)))


class Message(MessageBase, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    # "Session | None" would not be resolvable by SQLAlchemy
    session: Optional["Session"] = Relationship(back_populates="messages")
    session_id: UUID | None = Field(default=None, foreign_key="session.id", ondelete="CASCADE")
    parts: list[Part] = Relationship(
        back_populates="message", passive_deletes="all", sa_relationship_kwargs={"lazy": "selectin"}
    )
    usage: Usage | None = Relationship(
        back_populates="message", passive_deletes="all", sa_relationship_kwargs={"lazy": "selectin"}
    )
    instructions: str | None = Field(default=None, sa_column=Column(String))
    state: dict[str, object] | None = Field(default=None, sa_column=Column(JSON(none_as_null=True)))

    @classmethod
    def from_model_request(cls, session_id: UUID, request: ModelRequest) -> Self:
        parts = [Part.from_model_request_part(p) for p in request.parts]
        return cls(
            kind=MessageKind.REQUEST,
            session_id=session_id,
            instructions=request.instructions,
            parts=parts,
        )

    @classmethod
    def from_model_response(cls, session_id: UUID, response: ModelResponse) -> Self:
        parts = [Part.from_model_response_part(p) for p in response.parts]
        return cls(kind=MessageKind.RESPONSE, session_id=session_id, parts=parts)

    def to_dict(self) -> Mapping[str, object]:
        parts = [p.model_dump(mode="json", exclude={"message"}) for p in self.parts]
        usage = self.usage.model_dump(mode="json", exclude={"message"}) if self.usage else None
        return {
            **self.model_dump(mode="json", exclude={"parts", "usage", "session"}),
            "parts": parts,
            "usage": usage,
            "state": self.state,
        }
