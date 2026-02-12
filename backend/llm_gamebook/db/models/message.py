import enum
from collections.abc import Mapping, Sequence
from datetime import datetime
from typing import TYPE_CHECKING, Optional, Self
from uuid import UUID, uuid4

from pydantic_ai import ModelMessage, ModelResponse
from sqlalchemy import Column, Enum, String
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
    timestamp: datetime | None = None
    kind: MessageKind = Field(sa_column=Column(Enum(MessageKind)))
    model_name: str | None
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

    @classmethod
    def from_model_message(
        cls,
        message: ModelMessage,
        session_id: UUID,
        msg_id: UUID | None,
        part_ids: Sequence[UUID] | None,
        durations: dict[UUID, int] | None = None,
    ) -> Self:
        parts = list(Part.from_model_parts(message.parts, part_ids, durations))
        kind = MessageKind(message.kind)

        if isinstance(message, ModelResponse):
            finish_reason = (
                None if message.finish_reason is None else FinishReason(message.finish_reason)
            )
            return cls(
                id=msg_id or uuid4(),
                kind=kind,
                parts=parts,
                session_id=session_id,
                timestamp=message.timestamp,
                model_name=message.model_name,
                finish_reason=finish_reason,
                usage=Usage.from_request_usage(message.usage),
            )

        # ModelRequest
        return cls(
            id=msg_id or uuid4(),
            kind=kind,
            parts=parts,
            session_id=session_id,
            model_name=None,
            instructions=message.instructions,
            finish_reason=None,
        )

    def to_dict(self) -> Mapping[str, object]:
        parts = [p.model_dump(mode="json", exclude={"message"}) for p in self.parts]
        usage = self.usage.model_dump(mode="json", exclude={"message"}) if self.usage else None
        return {
            **self.model_dump(mode="json", exclude={"parts", "usage", "session"}),
            "parts": parts,
            "usage": usage,
        }
