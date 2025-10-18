from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from llm_gamebook.constants import PROJECT_NAME
from llm_gamebook.db import create_db_and_tables
from llm_gamebook.web.api import api_router
from llm_gamebook.web.engine_manager import EngineManager


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator:
    await create_db_and_tables()
    app.state.engine_mgr = EngineManager()
    yield
    await app.state.engine_mgr.close()


app = FastAPI(title=PROJECT_NAME, lifespan=lifespan)


@app.get("/", include_in_schema=False)
async def get() -> HTMLResponse:
    return HTMLResponse("")


app.include_router(api_router, prefix="/api")
