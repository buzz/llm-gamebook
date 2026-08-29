import enum

from sqlalchemy import Column, Enum
from sqlmodel import Field, SQLModel

from llm_gamebook.constants import DEFAULT_MAX_STATE_HISTORY


class ChatView(enum.StrEnum):
    STANDARD = "standard"
    DETAILS = "details"
    DEBUG = "debug"


class UserSettings(SQLModel, table=True):
    # id: Literal["settings"] = Field(default="settings", primary_key=True)
    id: str = Field(default="settings", primary_key=True)
    chat_view: ChatView = Field(
        sa_column=Column(Enum(ChatView)),
        default=ChatView.STANDARD,
        description="The view mode for chat display",
    )
    enter_submits_message: bool = Field(
        default=True, description="Whether Enter key submits a message"
    )
    max_state_history: int = Field(
        default=DEFAULT_MAX_STATE_HISTORY,
        ge=1,
        description="Maximum number of state snapshots to keep per session",
    )
