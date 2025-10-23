from collections.abc import AsyncGenerator
from typing import TYPE_CHECKING, Annotated
from uuid import UUID

from fastapi import Depends, Request, WebSocket
from sqlmodel.ext.asyncio.session import AsyncSession as AsyncDbSession

from llm_gamebook.db import db_engine
from llm_gamebook.message_bus import MessageBus
from llm_gamebook.web.get_model_tmp import get_model_state

if TYPE_CHECKING:
    from llm_gamebook.engine import EngineManager, StoryEngine


async def _get_db() -> AsyncGenerator[AsyncDbSession]:
    async with AsyncDbSession(db_engine) as session:
        yield session


DbSessionDep = Annotated[AsyncDbSession, Depends(_get_db)]


def _get_message_bus_ws(ws: WebSocket) -> MessageBus:
    return ws.app.state.bus


MessageBusDepWs = Annotated[MessageBus, Depends(_get_message_bus_ws)]


async def _get_engine(mgr: "EngineManager", session_id: UUID) -> "StoryEngine":
    model, state = get_model_state()
    return await mgr.get_or_create(session_id, model, state)


async def _get_engine_mgr_ws(ws: WebSocket) -> "EngineManager":
    return ws.app.state.engine_mgr


EngineMgrDepWs = Annotated["EngineManager", Depends(_get_engine_mgr_ws)]


async def _get_engine_rest(request: Request, session_id: UUID) -> "StoryEngine":
    return await _get_engine(request.app.state.engine_mgr, session_id)


EngineDepRest = Annotated["StoryEngine", Depends(_get_engine_rest)]
