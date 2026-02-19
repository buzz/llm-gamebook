from pydantic import BaseModel, field_validator


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
