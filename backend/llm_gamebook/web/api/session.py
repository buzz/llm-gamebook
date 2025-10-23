from fastapi import APIRouter, HTTPException

from llm_gamebook.db.crud.session import create_session as crud_create_session
from llm_gamebook.db.crud.session import get_session_count, get_sessions
from llm_gamebook.db.models import Message
from llm_gamebook.db.models import Session as SqlModelSession
from llm_gamebook.logger import logger

from .deps import DbSessionDep, EngineDepRest
from .models import (
    ModelRequest,
    ModelRequestCreate,
    ServerMessage,
    Session,
    SessionCreate,
    SessionFull,
    Sessions,
)

_log = logger.getChild("api")

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.get("/")
async def read_sessions(db_session: DbSessionDep, skip: int = 0, limit: int = 100) -> Sessions:
    return Sessions(
        data=[Session(**s.model_dump()) for s in await get_sessions(db_session, skip, limit)],
        count=await get_session_count(db_session),
    )


@router.get("/{session_id}", response_model=SessionFull)
async def read_session(engine: EngineDepRest, db_session: DbSessionDep) -> SqlModelSession:
    session = await engine.session_adapter.get_session(db_session)
    if not session:
        raise HTTPException(status_code=404, detail="Story session not found")
    return session


@router.post("/", response_model=Session)
async def create_session(db_session: DbSessionDep, session_in: SessionCreate) -> SqlModelSession:
    session_db = SqlModelSession(**session_in.model_dump())
    return await crud_create_session(db_session, session_db)


@router.post("/{session_id}/request", response_model=ModelRequest)
async def create_model_request(
    engine: EngineDepRest, db_session: DbSessionDep, message_in: ModelRequestCreate
) -> Message:
    return await engine.session_adapter.create_user_request(db_session, message_in)


@router.delete("/{session_id}")
async def delete_session(engine: EngineDepRest, db_session: DbSessionDep) -> ServerMessage:
    await engine.session_adapter.delete_session(db_session)
    return ServerMessage(message="Story session deleted successfully.")
