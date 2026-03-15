from typing import TypedDict, Unpack

from sqlmodel.ext.asyncio.session import AsyncSession as AsyncDbSession

from llm_gamebook.db.models import UserSettings
from llm_gamebook.db.models.user_settings import ChatView


async def get_user_settings(db_session: AsyncDbSession) -> UserSettings | None:
    return await db_session.get(UserSettings, "settings")


async def create_default_user_settings(db_session: AsyncDbSession) -> UserSettings:
    settings = UserSettings(id="settings")
    db_session.add(settings)
    await db_session.commit()
    await db_session.refresh(settings)
    return settings


class UserSettingsUpdate(TypedDict):
    chat_view: ChatView
    enter_submits_message: bool


async def update_user_settings(
    db_session: AsyncDbSession, /, **kwargs: Unpack[UserSettingsUpdate]
) -> UserSettings:
    settings = await db_session.get(UserSettings, "settings")
    if not settings:
        settings = UserSettings(id="settings")
        db_session.add(settings)

    settings.chat_view = ChatView(kwargs["chat_view"])
    settings.enter_submits_message = kwargs["enter_submits_message"]

    await db_session.commit()
    await db_session.refresh(settings)
    return settings
