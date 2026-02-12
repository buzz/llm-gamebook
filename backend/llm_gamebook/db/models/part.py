import enum
import json
from collections.abc import Iterable, Sequence
from contextlib import suppress
from datetime import datetime
from typing import TYPE_CHECKING, Final, Self
from uuid import UUID, uuid4

from pydantic_ai.messages import (
    ModelRequestPart,
    ModelResponsePart,
    SystemPromptPart,
    TextPart,
    ThinkingPart,
    ToolCallPart,
    ToolReturnPart,
    UserPromptPart,
)
from sqlalchemy import Column, Enum
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from llm_gamebook.db.models.message import Message

SUPPORTED_PARTS: Final = (
    SystemPromptPart,
    UserPromptPart,
    ToolCallPart,
    ToolReturnPart,
    TextPart,
    ThinkingPart,
)


class PartKind(enum.StrEnum):
    SYSTEM_PROMPT = "system-prompt"
    USER_PROMPT = "user-prompt"
    TEXT = "text"
    THINKING = "thinking"
    TOOL_CALL = "tool-call"
    TOOL_RETURN = "tool-return"


class PartBase(SQLModel):
    timestamp: datetime | None
    part_kind: PartKind = Field(sa_column=Column(Enum(PartKind)))
    content: str | None
    tool_name: str | None
    tool_call_id: str | None
    args: str | None
    duration_seconds: int | None = None


class Part(PartBase, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    message: "Message" = Relationship(back_populates="parts")
    message_id: UUID | None = Field(default=None, foreign_key="message.id", ondelete="CASCADE")

    @classmethod
    def from_model_parts(
        cls,
        parts: Sequence[ModelResponsePart | ModelRequestPart],
        part_ids: Sequence[UUID] | None = None,
        durations: dict[UUID, int] | None = None,
    ) -> Iterable[Self]:
        for idx, part in enumerate(parts):
            if not isinstance(part, SUPPORTED_PARTS):
                continue

            attrs = ("timestamp", "content", "tool_name", "tool_call_id", "args")
            kwargs = {a: getattr(part, a) for a in attrs if hasattr(part, a)}

            if isinstance(part, ToolCallPart) and not isinstance(kwargs.get("args"), str):
                kwargs["args"] = json.dumps(kwargs["args"])

            if part_ids is not None:
                with suppress(IndexError):
                    kwargs["id"] = part_ids[idx]

            if isinstance(part, ToolReturnPart):
                if isinstance(part.content, dict | list):
                    kwargs = {"content": json.dumps(part.content)}
                elif isinstance(part.content, str):
                    kwargs = {"content": part.content}
            elif isinstance(part, ThinkingPart) and durations is not None and part_ids is not None:
                with suppress(IndexError):
                    part_id = part_ids[idx]
                    if part_id in durations:
                        kwargs["duration_seconds"] = durations[part_id]

            yield cls(part_kind=PartKind(part.part_kind), **kwargs)
