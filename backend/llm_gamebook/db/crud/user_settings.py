from sqlmodel.ext.asyncio.session import AsyncSession as AsyncDbSession

from llm_gamebook.db.models import UserSettings
from llm_gamebook.db.models.user_settings import ChatView
from llm_gamebook.web.schemas.user_settings import UserSettingsUpdate


async def get_user_settings(db_session: AsyncDbSession) -> UserSettings | None:
    return await db_session.get(UserSettings, "settings")


async def create_default_user_settings(db_session: AsyncDbSession) -> UserSettings:
    settings = UserSettings(id="settings")
    db_session.add(settings)
    await db_session.commit()
    await db_session.refresh(settings)
    return settings


async def update_user_settings(
    db_session: AsyncDbSession, settings_update: UserSettingsUpdate
) -> UserSettings:
    settings = await db_session.get(UserSettings, "settings")
    if not settings:
        settings = UserSettings(id="settings")
        db_session.add(settings)

    settings.chat_view = ChatView(settings_update.chat_view)
    settings.enter_submits_message = settings_update.enter_submits_message
    await db_session.commit()
    await db_session.refresh(settings)
    return settings
