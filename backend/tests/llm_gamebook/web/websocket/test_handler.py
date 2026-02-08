import pytest
from fastapi import WebSocket
from sqlmodel.ext.asyncio.session import AsyncSession as AsyncDbSession

from llm_gamebook.db.models.session import Session
from llm_gamebook.engine.engine import StoryEngine
from llm_gamebook.engine.manager import EngineManager
from llm_gamebook.message_bus import MessageBus
from llm_gamebook.web.websocket.handler import WebSocketHandler


@pytest.mark.skip
async def test_handle_connection_success(
    websocket: WebSocket, db_session: AsyncDbSession, engine_mgr: EngineManager, bus: MessageBus
) -> None:
    pass


@pytest.mark.skip
async def test_handle_connection_disconnect(
    websocket: WebSocket, db_session: AsyncDbSession, engine_mgr: EngineManager, bus: MessageBus
) -> None:
    pass


@pytest.mark.skip
async def test_handle_connection_error(
    websocket: WebSocket, db_session: AsyncDbSession, engine_mgr: EngineManager, bus: MessageBus
) -> None:
    pass


@pytest.mark.skip
async def test_send_introduction_if_needed_new_session(
    engine: StoryEngine, db_session: AsyncDbSession
) -> None:
    pass


@pytest.mark.skip
async def test_send_introduction_if_needed_existing_session(
    engine: StoryEngine, db_session: AsyncDbSession
) -> None:
    pass


@pytest.mark.skip
async def test_handle_messages_ping(websocket: WebSocket, handler: WebSocketHandler) -> None:
    pass


@pytest.mark.skip
async def test_handle_messages_invalid_json(
    websocket: WebSocket, handler: WebSocketHandler
) -> None:
    pass


@pytest.mark.skip
async def test_generate_response_success(engine: StoryEngine, db_session: AsyncDbSession) -> None:
    pass


@pytest.mark.skip
async def test_generate_response_api_error(engine: StoryEngine, db_session: AsyncDbSession) -> None:
    pass


@pytest.mark.skip
async def test_on_engine_created(handler: WebSocketHandler, session: Session) -> None:
    pass


@pytest.mark.skip
async def test_on_engine_created_invalid_type(handler: WebSocketHandler) -> None:
    pass


@pytest.mark.skip
async def test_on_engine_response_user_request(handler: WebSocketHandler, session: Session) -> None:
    pass


@pytest.mark.skip
async def test_on_engine_response_started(handler: WebSocketHandler, session: Session) -> None:
    pass


@pytest.mark.skip
async def test_on_engine_response_stopped(handler: WebSocketHandler, session: Session) -> None:
    pass


@pytest.mark.skip
async def test_on_engine_response_error(handler: WebSocketHandler) -> None:
    pass


@pytest.mark.skip
async def test_on_engine_response_stream(handler: WebSocketHandler) -> None:
    pass
