from fastapi import APIRouter, WebSocket

router = APIRouter(prefix="/ws")


@router.websocket("/")
async def websocket_endpoint(websocket: WebSocket) -> None:
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Message text was: {data}")
