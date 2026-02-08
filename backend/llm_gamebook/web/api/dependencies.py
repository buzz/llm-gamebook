from collections.abc import AsyncIterator
from typing import Annotated
from uuid import UUID

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlmodel.ext.asyncio.session import AsyncSession as AsyncDbSession

from llm_gamebook.engine import EngineManager, StoryEngine
from llm_gamebook.web.get_model import get_model_state


def _get_db_engine(request: Request) -> AsyncEngine:
    db_engine = request.app.state.db_engine
    if not isinstance(db_engine, AsyncEngine):
        msg = "db_engine not found"
        raise TypeError(msg)

    return db_engine


DbEngineDep = Annotated[AsyncEngine, Depends(_get_db_engine)]


async def _get_db_session(db_engine: DbEngineDep) -> AsyncIterator[AsyncDbSession]:
    async with AsyncDbSession(db_engine) as session:
        yield session


DbSessionDep = Annotated[AsyncDbSession, Depends(_get_db_session)]


async def _get_story_engine(
    request: Request, session_id: UUID, db_session: DbSessionDep
) -> StoryEngine:
    engine_manager = request.app.state.engine_mgr
    if not isinstance(engine_manager, EngineManager):
        msg = "engine_mgr not found"
        raise TypeError(msg)

    model, state = await get_model_state(db_session, session_id)
    return await engine_manager.get_or_create(session_id, model, state)


StoryEngineDep = Annotated[StoryEngine, Depends(_get_story_engine)]
