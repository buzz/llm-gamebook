from fastapi import APIRouter, WebSocket

from .dependencies import DbSessionDep, MessageBusDep, StoryEngineManagerDep
from .handler import WebSocketHandler

websocket_router = APIRouter()


@websocket_router.websocket("")
async def websocket_endpoint(
    websocket: WebSocket,
    db_session: DbSessionDep,
    story_engine_manager: StoryEngineManagerDep,
    message_bus: MessageBusDep,
) -> None:
    """WebSocket endpoint for chat sessions."""
    handler = WebSocketHandler(db_session, story_engine_manager, message_bus)
    await handler.handle_connection(websocket)
