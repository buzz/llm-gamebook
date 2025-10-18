import contextlib

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from llm_gamebook.web.api.deps import EngineDepWs

from .models import MessageRead, MessageUpdate

router = APIRouter(prefix="/ws")


@router.websocket("/{chat_id}")
async def websocket_endpoint(websocket: WebSocket, engine: EngineDepWs) -> None:
    with contextlib.suppress(WebSocketDisconnect):
        await websocket.accept()

        message = await engine.generate_llm_message()
        update = MessageUpdate(
            event="llm_message", finish_reason="stop", message=MessageRead.model_validate(message)
        )
        await websocket.send_text(update.model_dump_json())

        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Message text was: {data}")
