from typing import TYPE_CHECKING, Self
from uuid import UUID, uuid4

from pydantic_ai.usage import RequestUsage
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .message import Message


class UsageBase(SQLModel):
    input_tokens: int
    output_tokens: int
    cache_write_tokens: int
    cache_read_tokens: int


class Usage(UsageBase, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    message: "Message" = Relationship(back_populates="usage")
    message_id: UUID = Field(foreign_key="message.id", ondelete="CASCADE")

    @classmethod
    def from_request_usage(cls, usage: RequestUsage) -> Self:
        return cls(
            input_tokens=usage.input_tokens,
            output_tokens=usage.output_tokens,
            cache_read_tokens=usage.cache_read_tokens,
            cache_write_tokens=usage.cache_write_tokens,
        )
