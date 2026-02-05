from collections.abc import Sequence
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from llm_gamebook.web.schemas.session.message import ModelMessage


class BaseSession(BaseModel):
    title: str | None = None
    """An optional session title."""


class SessionCreate(BaseSession):
    """Create fields for a session."""

    config_id: UUID
    """The ID of the model config associated with this session."""


class Session(BaseSession):
    """A chat session with an LLM."""

    id: UUID

    config_id: UUID | None = None
    """The ID of the model config associated with this session."""

    timestamp: datetime = Field(default_factory=datetime.now)
    """The timestamp of the session."""


class SessionUpdate(BaseSession):
    """Update fields for a session."""

    id: UUID

    config_id: UUID | None = None
    """The ID of the model config associated with this session."""


class SessionFull(Session):
    """A chat session with an LLM including the message history."""

    messages: Sequence[ModelMessage]


class Sessions(BaseModel):
    """A list of sessions."""

    data: Sequence[Session]
    count: int
