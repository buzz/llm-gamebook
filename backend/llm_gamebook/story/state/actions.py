from pydantic import BaseModel, ConfigDict, field_validator


class GenericPayload(BaseModel):
    """A payload accepting arbitrary key-value data, e.g. trigger action args."""

    model_config = ConfigDict(extra="allow")


class Action[T: BaseModel](BaseModel):
    """Base action class with name discriminator and typed payload."""

    name: str
    payload: T

    @field_validator("name", mode="before")
    @classmethod
    def validate_name(cls, v: object) -> object:
        if isinstance(v, str) and "/" not in v:
            msg = "Action name must be in format 'namespace/action'"
            raise ValueError(msg)
        return v


class EndGamePayload(BaseModel):
    """Payload for EndGameAction."""

    reason: str | None = None


class EndGameAction(Action[EndGamePayload]):
    """Action for ending the game session."""

    def __init__(self, reason: str | None = None) -> None:
        super().__init__(name="core/end-game", payload=EndGamePayload(reason=reason))


class ResetGamePayload(BaseModel):
    """Empty payload for ResetGameAction (takes no arguments)."""


class ResetGameAction(Action[ResetGamePayload]):
    """Action for resetting the game session to project defaults."""

    def __init__(self) -> None:
        super().__init__(name="core/reset-game", payload=ResetGamePayload())


class StepPayload(BaseModel):
    """Payload for actions targeting a point in the session history.

    Attributes:
        step: The target step (0-based message index). -1 targets the latest.
    """

    step: int = -1


class RestoreAction(Action[StepPayload]):
    """Action for restoring the session to a previous history step."""

    def __init__(self, step: int = -1) -> None:
        super().__init__(name="core/restore", payload=StepPayload(step=step))


class ForkAction(Action[StepPayload]):
    """Action for forking a new session from a history step."""

    def __init__(self, step: int = -1) -> None:
        super().__init__(name="core/fork", payload=StepPayload(step=step))
