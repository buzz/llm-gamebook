import enum
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Optional, Self
from uuid import UUID, uuid4

from pydantic import TypeAdapter
from pydantic_ai import ModelMessage, ModelRequest, ModelResponse, RequestUsage
from sqlalchemy import JSON, Column, Enum, String
from sqlmodel import Field, Relationship, SQLModel

from .part import Part
from .usage import Usage

if TYPE_CHECKING:
    from .session import Session

ModelMessageTypeAdapter: TypeAdapter[ModelMessage] = TypeAdapter(ModelMessage)


class MessageKind(enum.StrEnum):
    REQUEST = "request"
    RESPONSE = "response"


class FinishReason(enum.StrEnum):
    STOP = "stop"
    LENGTH = "length"
    CONTENT_FILTER = "content_filter"
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
        return cls(
            kind=MessageKind.RESPONSE,
            session_id=session_id,
            parts=parts,
            finish_reason=FinishReason(response.finish_reason) if response.finish_reason else None,
        )

    def to_model_message(self) -> ModelMessage:
        msg_dict = self.model_dump(mode="json", exclude={"parts", "usage", "session"})
        msg = ModelMessageTypeAdapter.validate_python({**msg_dict, "parts": []})

        if isinstance(msg, ModelResponse):
            if self.usage:
                usage = self.usage.model_dump(mode="json", exclude={"message"})
                msg.usage = RequestUsage(**usage)
            if self.parts:
                msg.parts = [p.to_model_response_part() for p in self.parts]

        elif isinstance(msg, ModelRequest):
            if self.parts:
                msg.parts = [p.to_model_request_part() for p in self.parts]

        return msg
