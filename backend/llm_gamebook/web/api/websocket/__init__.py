from typing import TYPE_CHECKING
from uuid import UUID

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.websockets import WebSocketState
from openai import APIError
from pydantic import TypeAdapter, ValidationError
from sqlmodel.ext.asyncio.session import AsyncSession as AsyncDbSession

from llm_gamebook.logger import logger
from llm_gamebook.message_bus import BusSubscriber, MessageBus
from llm_gamebook.web.api.deps import DbSessionDep, EngineMgrDepWs, MessageBusDepWs
from llm_gamebook.web.get_model_tmp import get_model_state

from .models import (
    WebSocketClientMessage,
    WebSocketErrorMessage,
    WebSocketPingMessage,
    WebSocketPongMessage,
    WebSocketServerMessage,
    WebSocketStatusMessage,
    WebSocketStreamMessage,
)

if TYPE_CHECKING:
    from llm_gamebook.engine.engine import (
        ResponseErrorBusMessage,
        StoryEngine,
        StreamUpdateBusMessage,
    )
    from llm_gamebook.engine.manager import EngineManager

router = APIRouter(prefix="/ws")

client_msg_adapter = TypeAdapter[WebSocketClientMessage](WebSocketClientMessage)

_log = logger.getChild("websocket")


class WebSocketHandler(BusSubscriber):
    """Handles WebSocket connections for chat sessions."""

    def __init__(
        self, engine_mgr: "EngineManager", db_session: AsyncDbSession, bus: MessageBus
    ) -> None:
        self._engine_mgr = engine_mgr
        self._db_session = db_session
        self._bus = bus
        self._websocket: WebSocket

        self._subscribe("engine.created", self._on_engine_created)
        self._subscribe("engine.response.user_request", self._on_engine_response_user_request)
        self._subscribe("engine.response.started", self._on_engine_response_started)
        self._subscribe("engine.response.stopped", self._on_engine_response_stopped)
        self._subscribe("engine.response.error", self._on_engine_response_error)
        self._subscribe("engine.response.stream", self._on_engine_response_stream)

    async def handle_connection(self, websocket: WebSocket) -> None:
        """Main connection handler for WebSocket connections."""
        try:
            self._websocket = websocket
            await self._websocket.accept()
            await self._handle_messages()
        except WebSocketDisconnect:
            pass
        except Exception as exc:
            error_message = WebSocketErrorMessage(
                name=type(exc).__name__,
                message=str(exc),
            )
            await self._send_message(error_message)
            raise
        finally:
            self.close()

    async def _send_introduction_if_needed(self, session_id: UUID) -> None:
        """Generate introduction message if this is a new session."""
        engine = self._engine_mgr.get(session_id)
        message_count = await engine.session_adapter.get_message_count(self._db_session)
        if message_count == 0:
            await self._generate_response(engine)

    async def _handle_messages(self) -> None:
        """Handle incoming WebSocket messages."""
        while True:
            data = await self._websocket.receive_text()
            try:
                msg = client_msg_adapter.validate_json(data)
            except ValidationError:
                _log.exception("Malformed client message received")
            else:
                if isinstance(msg, WebSocketPingMessage):
                    await self._send_message(WebSocketPongMessage())

    async def _generate_response(self, engine: "StoryEngine") -> None:
        """Generate response from engine and notify Web UI."""
        try:
            await engine.generate_response(self._db_session, streaming=True)
        except APIError as err:
            msg = WebSocketErrorMessage(
                name=type(err).__name__,
                message=err.message,
            )
            await self._send_message(msg)

    async def _get_engine(self, session_id: UUID) -> "StoryEngine":
        model, state = get_model_state()
        return await self._engine_mgr.get_or_create(session_id, model, state)

    async def _send_message(self, message: WebSocketServerMessage) -> None:
        """Send a WebSocket message."""
        if self._websocket.client_state == WebSocketState.CONNECTED:
            await self._websocket.send_text(message.model_dump_json())
        else:
            _log.warning("Trying to send message while not connected")

    async def _on_engine_created(self, session_id: UUID) -> None:
        await self._send_introduction_if_needed(session_id)

    async def _on_engine_response_user_request(self, session_id: UUID) -> None:
        await self._generate_response(self._engine_mgr.get(session_id))

    async def _on_engine_response_started(self, session_id: UUID) -> None:
        await self._send_message(WebSocketStatusMessage(session_id=session_id, status="started"))

    async def _on_engine_response_stopped(self, session_id: UUID) -> None:
        await self._send_message(WebSocketStatusMessage(session_id=session_id, status="stopped"))

    async def _on_engine_response_error(self, msg: "ResponseErrorBusMessage") -> None:
        ws_msg = WebSocketErrorMessage.from_exception(msg["session_id"], msg["error"])
        await self._send_message(ws_msg)

    async def _on_engine_response_stream(self, msg: "StreamUpdateBusMessage") -> None:
        await self._send_message(WebSocketStreamMessage.from_stream_update(msg))


@router.websocket("")
async def websocket_endpoint(
    websocket: WebSocket, mgr: EngineMgrDepWs, db_session: DbSessionDep, bus: MessageBusDepWs
) -> None:
    """WebSocket endpoint for chat sessions."""
    await WebSocketHandler(mgr, db_session, bus).handle_connection(websocket)
