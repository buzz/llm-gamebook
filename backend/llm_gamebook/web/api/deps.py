from collections.abc import AsyncGenerator
from pathlib import Path
from typing import Annotated
from uuid import UUID

from fastapi import Depends, Request, WebSocket
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider
from sqlmodel.ext.asyncio.session import AsyncSession

from llm_gamebook.db import db_engine
from llm_gamebook.engine import StoryEngine
from llm_gamebook.story.project import Project
from llm_gamebook.story.state import StoryState
from llm_gamebook.web.engine_manager import EngineManager


async def _get_db() -> AsyncGenerator[AsyncSession]:
    async with AsyncSession(db_engine) as session:
        yield session


DbSessionDep = Annotated[AsyncSession, Depends(_get_db)]


async def _get_engine(mgr: EngineManager, chat_id: UUID) -> StoryEngine:
    path = Path("/home/buzz/llm/llm-gamebook/llm-gamebook/examples/broken-bulb")
    state = StoryState(Project.from_path(path))
    provider = OpenAIProvider(base_url="http://localhost:5001/v1", api_key="123")
    model = OpenAIChatModel("Qwen3-4B", provider=provider)
    return await mgr.get_or_create(chat_id, model, state, streaming=False)


async def _get_engine_ws(ws: WebSocket, chat_id: UUID) -> StoryEngine:
    return await _get_engine(ws.app.state.engine_mgr, chat_id)


EngineDepWs = Annotated[StoryEngine, Depends(_get_engine_ws)]


async def _get_engine_rest(request: Request, chat_id: UUID) -> StoryEngine:
    return await _get_engine(request.app.state.engine_mgr, chat_id)


EngineDepRest = Annotated[StoryEngine, Depends(_get_engine_rest)]
