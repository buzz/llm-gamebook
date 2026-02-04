import enum
from collections.abc import Mapping, Sequence
from datetime import datetime
from typing import TYPE_CHECKING, Any, Self
from uuid import UUID, uuid4

from pydantic_ai import ModelMessage, ModelResponse
from sqlalchemy import Column, Enum
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
    session: "Session" = Relationship(back_populates="messages")
    session_id: UUID | None = Field(foreign_key="session.id", ondelete="CASCADE")
    parts: list[Part] = Relationship(
        back_populates="message", passive_deletes="all", sa_relationship_kwargs={"lazy": "selectin"}
    )
    usage: Usage | None = Relationship(
        back_populates="message", passive_deletes="all", sa_relationship_kwargs={"lazy": "selectin"}
    )

    @classmethod
    def from_model_message(
        cls,
        message: ModelMessage,
        session_id: UUID,
        msg_id: UUID | None,
        part_ids: Sequence[UUID] | None,
        durations: dict[UUID, int] | None = None,
    ) -> Self:
        kwargs = {
            "kind": message.kind,
            "parts": list(Part.from_model_parts(message.parts, part_ids, durations)),
            "session_id": session_id,
        }
        if msg_id:
            kwargs["id"] = msg_id

        if isinstance(message, ModelResponse):
            return cls(
                **kwargs,
                timestamp=message.timestamp,
                model_name=message.model_name,
                finish_reason=message.finish_reason,
                usage=Usage.from_request_usage(message.usage),
            )
        # ModelRequest
        return cls(**kwargs)

    def to_dict(self) -> Mapping[str, Any]:
        parts = [p.model_dump(mode="json", exclude={"message"}) for p in self.parts]
        usage = self.usage.model_dump(mode="json", exclude={"message"}) if self.usage else None
        return {
            **self.model_dump(mode="json", exclude={"parts", "usage", "session"}),
            "parts": parts,
            "usage": usage,
        }
