from fastapi import APIRouter

from llm_gamebook.db.crud.user_settings import (
    create_default_user_settings,
    get_user_settings,
    update_user_settings,
)
from llm_gamebook.db.models.user_settings import ChatView
from llm_gamebook.web.api.dependencies import DbSessionDep
from llm_gamebook.web.schemas.common import ServerMessage
from llm_gamebook.web.schemas.user_settings import UserSettings

from ._tags import ApiTags

settings_router = APIRouter(prefix="/settings", tags=[ApiTags.settings])


@settings_router.get("/", response_model=UserSettings)
async def read_settings(db_session: DbSessionDep) -> UserSettings:
    settings = await get_user_settings(db_session)
    if not settings:
        settings = await create_default_user_settings(db_session)
    return UserSettings.model_validate(settings, from_attributes=True)


@settings_router.put("/", response_model=ServerMessage)
async def update_settings(db_session: DbSessionDep, settings_update: UserSettings) -> ServerMessage:
    await update_user_settings(
        db_session,
        chat_view=ChatView(settings_update.chat_view),
        enter_submits_message=settings_update.enter_submits_message,
    )
    return ServerMessage(message="Settings updated successfully.")
