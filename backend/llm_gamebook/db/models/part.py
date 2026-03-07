import enum
import json
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Final, Self
from uuid import UUID, uuid4

from pydantic import TypeAdapter
from pydantic_ai import ModelRequestPart, RetryPromptPart
from pydantic_ai.messages import (
    ModelResponsePart,
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

ModelRequestPartTypeAdapter: TypeAdapter[ModelRequestPart] = TypeAdapter(ModelRequestPart)
ModelResponsePartTypeAdapter: TypeAdapter[ModelResponsePart] = TypeAdapter(ModelResponsePart)

SUPPORTED_PARTS: Final = (
    UserPromptPart,
    ToolCallPart,
    ToolReturnPart,
    TextPart,
    ThinkingPart,
)


class PartKind(enum.StrEnum):
    USER_PROMPT = "user-prompt"
    TEXT = "text"
    THINKING = "thinking"
    TOOL_CALL = "tool-call"
    TOOL_RETURN = "tool-return"
    RETRY_PROMPT = "retry-prompt"


REQUEST_PART_KINDS: Final[set[PartKind]] = {
    PartKind.USER_PROMPT,
    PartKind.TOOL_RETURN,
    PartKind.RETRY_PROMPT,
}

RESPONSE_PART_KINDS: Final[set[PartKind]] = {
    PartKind.TEXT,
    PartKind.TOOL_CALL,
    PartKind.THINKING,
}


class PartBase(SQLModel):
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    kind: PartKind = Field(sa_column=Column(Enum(PartKind)))
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
    def from_model_request_part(cls, request_part: ModelRequestPart) -> Self:
        if not isinstance(request_part, UserPromptPart | ToolReturnPart | RetryPromptPart):
            msg = f"Unsupported part type: {type(request_part).__name__}"
            raise TypeError(msg)

        part = cls(
            timestamp=request_part.timestamp,
            kind=PartKind(request_part.part_kind),
            content=None,
            tool_name=None,
            tool_call_id=None,
            args=None,
        )

        if isinstance(request_part, UserPromptPart):
            if not isinstance(request_part.content, str):
                msg = f"Unsupported content type: {type(request_part.content).__name__}"
                raise TypeError(msg)
            part.content = request_part.content

        elif isinstance(request_part, ToolReturnPart):
            part.tool_name = request_part.tool_name
            part.tool_call_id = request_part.tool_call_id

            if isinstance(request_part.content, dict | list):
                part.content = json.dumps(request_part.content)
            elif isinstance(request_part.content, str):
                part.content = request_part.content
            else:
                msg = f"Unsupported content type: {type(request_part.content).__name__}"
                raise TypeError(msg)

        elif isinstance(request_part, RetryPromptPart):
            part.tool_name = request_part.tool_name
            part.tool_call_id = request_part.tool_call_id

            if not isinstance(request_part.content, str):
                msg = f"Unsupported content type: {type(request_part.content).__name__}"
                raise TypeError(msg)
            part.content = request_part.content

        return part

    @classmethod
    def from_model_response_part(cls, response_part: ModelResponsePart) -> Self:
        if not isinstance(response_part, TextPart | ThinkingPart | ToolCallPart):
            msg = f"Unsupported part type: {type(response_part).__name__}"
            raise TypeError(msg)

        part = cls(
            kind=PartKind(response_part.part_kind),
            content=None,
            tool_name=None,
            tool_call_id=None,
            args=None,
        )

        if isinstance(response_part, TextPart | ThinkingPart):
            part.content = response_part.content

        elif isinstance(response_part, ToolCallPart):
            part.tool_name = response_part.tool_name
            part.tool_call_id = response_part.tool_call_id

            if isinstance(response_part.args, dict | list):
                part.args = json.dumps(response_part.args)
            else:
                part.args = response_part.args

        return part

    def to_model_request_part(self) -> ModelRequestPart:
        if self.kind not in REQUEST_PART_KINDS:
            msg = f"Expected kind '{self.kind}' to be one of: {REQUEST_PART_KINDS}"
            raise ValueError(msg)

        return ModelRequestPartTypeAdapter.validate_python({
            **self.model_dump(exclude={"id", "kind"}),
            "id": str(self.id),
            "part_kind": self.kind,
        })

    def to_model_response_part(self) -> ModelResponsePart:
        if self.kind not in RESPONSE_PART_KINDS:
            msg = f"Expected kind '{self.kind}' to be one of: {RESPONSE_PART_KINDS}"
            raise ValueError(msg)

        return ModelResponsePartTypeAdapter.validate_python({
            **self.model_dump(exclude={"id", "kind"}),
            "id": str(self.id),
            "part_kind": self.kind,
        })
