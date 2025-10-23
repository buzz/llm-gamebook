from collections.abc import Sequence
from datetime import datetime
from typing import Annotated, Literal
from uuid import UUID

import pydantic_core
from pydantic import BaseModel, Discriminator, Field

from llm_gamebook.db.models import UsageBase
from llm_gamebook.db.models.message import FinishReason


class ServerMessage(BaseModel):
    message: str


class Usage(UsageBase):
    pass


# --- Parts ---
class SystemPromptPart(BaseModel):
    """A system prompt, generally written by the application developer.

    This gives the model context and guidance on how to respond.
    """

    id: UUID

    part_kind: Literal["system-prompt"] = "system-prompt"
    """Part type identifier, this is available on all parts as a discriminator."""

    content: str
    """The content of the prompt."""

    timestamp: datetime
    """The timestamp of the prompt."""


class BaseUserPromptPart(BaseModel):
    part_kind: Literal["user-prompt"] = "user-prompt"
    """Part type identifier, this is available on all parts as a discriminator."""

    content: str
    """The content of the prompt."""


class UserPromptPartCreate(BaseUserPromptPart):
    timestamp: datetime | None = None
    """The timestamp of the prompt."""


class UserPromptPart(BaseUserPromptPart):
    """A user prompt, generally written by the user."""

    id: UUID

    timestamp: datetime
    """The timestamp of the prompt."""


class ToolReturnPart(BaseModel):
    """A tool return message, this encodes the result of running a tool."""

    id: UUID

    part_kind: Literal["tool-return"] = "tool-return"
    """Part type identifier, this is available on all parts as a discriminator."""

    tool_name: str | None
    """The name of the "tool" was called."""

    content: str
    """The return value."""

    tool_call_id: str | None
    """The tool call identifier."""

    timestamp: datetime | None
    """The timestamp, when the tool returned."""


class RetryPromptPart(BaseModel):
    """A message sent back to an LLM asking it to try again."""

    id: UUID

    part_kind: Literal["retry-prompt"] = "retry-prompt"
    """Part type identifier, this is available on all parts as a discriminator."""

    content: Sequence[pydantic_core.ErrorDetails] | str
    """Details of why and how the model should retry.

    If the retry was triggered by a ValidationError, this will be a list of error details.
    """

    tool_name: str | None = None
    """The name of the tool that was called, if any."""

    tool_call_id: str
    """The tool call identifier."""

    timestamp: datetime
    """The timestamp, when the retry was triggered."""


type ModelRequestPart = Annotated[
    SystemPromptPart | UserPromptPart | ToolReturnPart | RetryPromptPart,
    Discriminator("part_kind"),
]
"""A message part sent to an LLM."""


class TextPart(BaseModel):
    """A plain text response from an LLM."""

    id: UUID

    part_kind: Literal["text"] = "text"
    """Part type identifier, this is available on all parts as a discriminator."""

    content: str
    """The text content of the response."""


class ToolCallPart(BaseModel):
    """A tool call from an LLM."""

    id: UUID

    part_kind: Literal["tool-call"] = "tool-call"
    """Part type identifier, this is available on all parts as a discriminator."""

    tool_name: str
    """The name of the tool to call."""

    args: str | None = None
    """The arguments to pass to the tool."""

    tool_call_id: str
    """The tool call identifier."""


class ThinkingPart(BaseModel):
    """A thinking response from an LLM."""

    id: UUID

    part_kind: Literal["thinking"] = "thinking"
    """Part type identifier, this is available on all parts as a discriminator."""

    content: str
    """The thinking content of the response."""

    provider_name: str | None = None
    """The name of the provider that generated the response."""


type ModelResponsePart = Annotated[
    TextPart | ToolCallPart | ThinkingPart,
    Discriminator("part_kind"),
]
"""A message part returned by an LLM."""


# --- Message ---
class BaseModelRequest(BaseModel):
    kind: Literal["request"] = "request"
    """Message type identifier, this is available on all parts as a discriminator."""


class ModelRequestCreate(BaseModelRequest):
    parts: Sequence[UserPromptPartCreate]


class ModelRequest(BaseModelRequest):
    """A request sent to an LLM."""

    id: UUID

    parts: Sequence[ModelRequestPart]
    """The parts of the user message."""

    instructions: str | None = None
    """The instructions for the model."""


class ModelResponse(BaseModel):
    """A response from an LLM."""

    id: UUID

    kind: Literal["response"] = "response"
    """Message type identifier, this is available on all parts as a discriminator."""

    parts: Sequence[ModelResponsePart]
    """The parts of the model message."""

    usage: Usage
    """Usage information for the request."""

    model_name: str | None = None
    """The name of the model that generated the response."""

    timestamp: datetime
    """The timestamp of the response."""

    provider_name: str | None = None
    """The name of the LLM provider that generated the response."""

    finish_reason: FinishReason | None = None
    """Reason the model finished generating the response."""


type ModelMessage = Annotated[ModelRequest | ModelResponse, Discriminator("kind")]
"""Any message sent to or returned by an LLM."""


# --- Session ---
class BaseSession(BaseModel):
    title: str | None = None
    """An optional session title."""


class SessionCreate(BaseSession):
    timestamp: datetime | None = None
    """The timestamp of the session."""


class Session(BaseSession):
    """A chat session with an LLM."""

    id: UUID

    timestamp: datetime = Field(default_factory=datetime.now)
    """The timestamp of the session."""


class SessionFull(Session):
    """A chat session with an LLM including the message history."""

    messages: Sequence[ModelMessage]


class Sessions(BaseModel):
    """A list of sessions."""

    data: Sequence[Session]
    count: int
