from datetime import datetime

from pydantic import Field

from llm_gamebook.web.schemas.base import CamelCasedBaseModel


class StepRequest(CamelCasedBaseModel):
    """Request body for core actions targeting a point in the session history."""

    step: int = Field(ge=-1)
    """The target step (0-based message index) or -1 for the latest state."""


class EndGameRequest(CamelCasedBaseModel):
    """Request body for ending a game session."""

    reason: str | None = None
    """An optional human-readable reason for ending the game."""


class StateEntry(CamelCasedBaseModel):
    """A single stored state snapshot in a session's history."""

    step: int
    """The 0-based index of the snapshot's message within the session's messages."""

    timestamp: datetime | None = None
    """The timestamp of the snapshot's message."""

    field_count: int
    """The number of entity fields changed in this snapshot."""


class StateHistory(CamelCasedBaseModel):
    """A session's stored state snapshots in ascending step order."""

    data: list[StateEntry]
