from collections.abc import Sequence
from datetime import datetime
from typing import Annotated, Literal
from uuid import UUID

from pydantic import Discriminator

from llm_gamebook.db.models.message import FinishReason
from llm_gamebook.web.schemas.base import CamelCasedBaseModel

from .part import ModelRequestPart, ModelResponsePart


class Usage(CamelCasedBaseModel):
    input_tokens: int
    output_tokens: int
    cache_write_tokens: int
    cache_read_tokens: int


class BaseModelRequest(CamelCasedBaseModel):
    kind: Literal["request"] = "request"
    """Message type identifier, this is available on all parts as a discriminator."""


class ModelRequestCreate(CamelCasedBaseModel):
    content: str


class ModelRequest(BaseModelRequest):
    """A request sent to an LLM."""

    id: UUID

    parts: Sequence[ModelRequestPart]
    """The parts of the user message."""

    instructions: str | None = None
    """The instructions for the model."""


class ModelResponse(CamelCasedBaseModel):
    """A response from an LLM."""

    id: UUID

    kind: Literal["response"] = "response"
    """Message type identifier, this is available on all parts as a discriminator."""

    parts: Sequence[ModelResponsePart]
    """The parts of the model message."""

    usage: Usage | None = None
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
