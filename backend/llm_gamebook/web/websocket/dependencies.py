from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import Depends, WebSocket
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlmodel.ext.asyncio.session import AsyncSession as AsyncDbSession

from llm_gamebook.engine import EngineManager
from llm_gamebook.message_bus import MessageBus


def _get_db_engine(websocket: WebSocket) -> AsyncEngine:
    db_engine = websocket.app.state.db_engine
    if not isinstance(db_engine, AsyncEngine):
        msg = "db_engine not found"
        raise TypeError(msg)

    return db_engine


DbEngineDep = Annotated[AsyncEngine, Depends(_get_db_engine)]


async def _get_db_session(db_engine: DbEngineDep) -> AsyncIterator[AsyncDbSession]:
    async with AsyncDbSession(db_engine) as db_session:
        yield db_session


DbSessionDep = Annotated[AsyncDbSession, Depends(_get_db_session)]


def _get_message_bus(websocket: WebSocket) -> MessageBus:
    message_bus = websocket.app.state.bus
    if not isinstance(message_bus, MessageBus):
        msg = "Message bus not found"
        raise TypeError(msg)

    return message_bus


MessageBusDep = Annotated[MessageBus, Depends(_get_message_bus)]


async def _get_engine_mgr(websocket: WebSocket) -> EngineManager:
    engine_mgr = websocket.app.state.engine_mgr
    if not isinstance(engine_mgr, EngineManager):
        msg = "Engine manager not found"
        raise TypeError(msg)

    return engine_mgr


StoryEngineManagerDep = Annotated[EngineManager, Depends(_get_engine_mgr)]
