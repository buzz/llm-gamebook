import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from llm_gamebook.constants import PROJECT_NAME
from llm_gamebook.db import create_async_db_engine
from llm_gamebook.engine import EngineManager
from llm_gamebook.logger import setup_logger
from llm_gamebook.message_bus import MessageBus

from .api import api_router
from .schemas.websocket.openapi import add_websocket_schema
from .websocket import websocket_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    add_websocket_schema(app.openapi())

    async with (
        create_async_db_engine() as db_engine,
        MessageBus() as bus,
        EngineManager(bus) as engine_mgr,
    ):
        app.state.db_engine = db_engine
        app.state.bus = bus
        app.state.engine_mgr = engine_mgr
        yield


def create_app(log_file: Path | None = None, *, debug: bool = False) -> FastAPI:
    uvicorn_logger = logging.getLogger("uvicorn.error")
    log_level = logging.DEBUG if debug or uvicorn_logger.level <= logging.DEBUG else logging.INFO
    setup_logger("web", log_level, log_file)

    app = FastAPI(title=PROJECT_NAME, lifespan=lifespan)

    @app.get("/", include_in_schema=False)
    async def get() -> HTMLResponse:
        return HTMLResponse("")

    app.include_router(api_router, prefix="/api")
    app.include_router(websocket_router, prefix="/ws")

    return app
