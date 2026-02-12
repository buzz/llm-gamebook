from unittest.mock import AsyncMock

import pytest
from fastapi import WebSocket
from sqlmodel.ext.asyncio.session import AsyncSession as AsyncDbSession
from starlette.websockets import WebSocketState

from llm_gamebook.engine.manager import EngineManager
from llm_gamebook.message_bus import MessageBus
from llm_gamebook.web.websocket.handler import WebSocketHandler


@pytest.fixture
async def handler(
    db_session: AsyncDbSession, engine_manager: EngineManager, message_bus: MessageBus
) -> WebSocketHandler:
    return WebSocketHandler(db_session, engine_manager, message_bus)


@pytest.fixture
async def mock_websocket() -> AsyncMock:
    ws = AsyncMock(spec=WebSocket)
    ws.client_state = WebSocketState.CONNECTED
    ws.send_text = AsyncMock()
    ws.receive_text = AsyncMock()
    ws.accept = AsyncMock()
    return ws
