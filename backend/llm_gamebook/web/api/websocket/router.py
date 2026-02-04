from fastapi import APIRouter, WebSocket

from llm_gamebook.web.api.deps import DbSessionDep, EngineMgrDepWs, MessageBusDepWs

from .handler import WebSocketHandler

router = APIRouter(prefix="/ws")


@router.websocket("")
async def websocket_endpoint(
    websocket: WebSocket, mgr: EngineMgrDepWs, db_session: DbSessionDep, bus: MessageBusDepWs
) -> None:
    """WebSocket endpoint for chat sessions."""
    await WebSocketHandler(mgr, db_session, bus).handle_connection(websocket)
