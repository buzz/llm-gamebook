from uuid import UUID

from fastapi import APIRouter, HTTPException

from llm_gamebook.db.crud.model_config import get_model_config
from llm_gamebook.db.crud.session import create_session as crud_create_session
from llm_gamebook.db.crud.session import (
    get_session_count,
    get_sessions,
    update_session_model_config,
)
from llm_gamebook.db.models import Message
from llm_gamebook.db.models import Session as SqlModelSession
from llm_gamebook.engine.message import SessionModelConfigChangedMessage
from llm_gamebook.story.errors import ProjectNotFoundError
from llm_gamebook.web.schemas.common import ServerMessage
from llm_gamebook.web.schemas.session import (
    Session,
    SessionCreate,
    SessionFull,
    Sessions,
    SessionUpdate,
)
from llm_gamebook.web.schemas.session.message import ModelRequest, ModelRequestCreate

from .dependencies import DbSessionDep, MessageBusDep, ProjectManagerDep, StoryEngineDep

session_router = APIRouter(prefix="/sessions", tags=["sessions"])


@session_router.get("/")
async def read_sessions(
    db_session: DbSessionDep, project_id: str | None = None, skip: int = 0, limit: int = 100
) -> Sessions:
    sessions = await get_sessions(db_session, project_id, skip, limit)

    return Sessions(
        data=[Session.model_validate(s, from_attributes=True) for s in sessions],
        count=await get_session_count(db_session, project_id),
    )


@session_router.get("/{session_id}", response_model=SessionFull)
async def read_session(engine: StoryEngineDep, db_session: DbSessionDep) -> SqlModelSession:
    session = await engine.session_adapter.get_session(db_session)

    if not session:
        # If we get this far, the session must be available
        raise HTTPException(status_code=500, detail="Story session expected")

    return session


@session_router.post("/")
async def create_session(
    db_session: DbSessionDep, project_manager: ProjectManagerDep, session_in: SessionCreate
) -> Session:
    model_config = await get_model_config(db_session, session_in.config_id)
    if not model_config:
        raise HTTPException(status_code=404, detail="Model config not found")

    try:
        project = project_manager.get_project(session_in.project_id)
    except ProjectNotFoundError as err:
        raise HTTPException(status_code=404, detail="Project not found") from err

    session = await crud_create_session(db_session, model_config, project.id, session_in.title)

    return Session.model_validate({**session.model_dump(), "message_count": 0})


@session_router.patch("/{session_id}")
async def update_session(
    db_session: DbSessionDep,
    session_id: str,
    session_update: SessionUpdate,
    message_bus: MessageBusDep,
) -> ServerMessage:
    session_uuid = UUID(session_id)
    await update_session_model_config(db_session, session_uuid, session_update.config_id)

    if session_update.config_id:
        config = await get_model_config(db_session, session_update.config_id)
        if config:
            message_bus.publish(
                SessionModelConfigChangedMessage(
                    session_id=session_uuid,
                    model_name=config.model_name,
                    provider=config.provider,
                    base_url=config.base_url,
                    api_key=config.api_key,
                ),
            )

    return ServerMessage(message="Session updated successfully.")


@session_router.post("/{session_id}/request", response_model=ModelRequest)
async def create_model_request(
    engine: StoryEngineDep, db_session: DbSessionDep, message_in: ModelRequestCreate
) -> Message:
    return await engine.session_adapter.create_user_request(db_session, message_in)


@session_router.delete("/{session_id}")
async def delete_session(engine: StoryEngineDep, db_session: DbSessionDep) -> ServerMessage:
    await engine.session_adapter.delete_session(db_session)
    return ServerMessage(message="Story session deleted successfully.")
