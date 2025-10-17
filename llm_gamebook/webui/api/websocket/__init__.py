from datetime import UTC, datetime
from pathlib import Path
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, WebSocket
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider

from llm_gamebook.engine import StoryEngine
from llm_gamebook.story.project import Project
from llm_gamebook.story.state import StoryState
from llm_gamebook.webui.api.websocket.models import ServerLLMMessage

router = APIRouter(prefix="/ws")


def get_story_engine(chat_id: UUID) -> StoryEngine:
    path = Path("/home/buzz/llm/llm-gamebook/llm-gamebook/examples/broken-bulb")
    state = StoryState(Project.from_path(path))
    provider = OpenAIProvider(base_url="http://localhost:5001/v1", api_key="123")
    model = OpenAIChatModel("Qwen3-4B", provider=provider)
    return StoryEngine(chat_id, model, state, streaming=False)


EngineDep = Annotated[StoryEngine, Depends(get_story_engine)]


@router.websocket("/{chat_id}")
async def websocket_endpoint(websocket: WebSocket, chat_id: UUID, engine: EngineDep) -> None:
    await websocket.accept()

    msg_id, msg = await engine.generate_llm_message()
    ws_msg = ServerLLMMessage(
        id=msg_id, created_at=datetime.now(tz=UTC), thinking=msg.thinking, text=msg.text
    )
    await websocket.send_text(ws_msg.model_dump_json())

    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Message text was: {data}")
