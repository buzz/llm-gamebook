import enum

from sqlalchemy import Column, Enum
from sqlmodel import Field, SQLModel


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
