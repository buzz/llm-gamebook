from typing import TYPE_CHECKING
from uuid import UUID

from fastapi import WebSocket, WebSocketDisconnect
from fastapi.websockets import WebSocketState
from openai import APIError
from pydantic import TypeAdapter, ValidationError
from sqlmodel.ext.asyncio.session import AsyncSession as AsyncDbSession

from llm_gamebook.engine.message import (
    EngineCreated,
    ResponseErrorMessage,
    ResponseStartedMessage,
    ResponseStoppedMessage,
    ResponseStreamUpdateMessage,
    ResponseUserRequestMessage,
)
from llm_gamebook.logger import logger
from llm_gamebook.message_bus import BusSubscriber, MessageBus
from llm_gamebook.web.schema.websocket.message import (
    WebSocketClientMessage,
    WebSocketErrorMessage,
    WebSocketPingMessage,
    WebSocketPongMessage,
    WebSocketServerMessage,
    WebSocketStatusMessage,
    WebSocketStreamMessage,
)

if TYPE_CHECKING:
    from llm_gamebook.engine.engine import StoryEngine
    from llm_gamebook.engine.manager import EngineManager


client_msg_adapter = TypeAdapter[WebSocketClientMessage](WebSocketClientMessage)

_log = logger.getChild("websocket")


class WebSocketHandler(BusSubscriber):
    """Handles WebSocket connections for chat sessions."""

    def __init__(
        self, db_session: AsyncDbSession, engine_mgr: "EngineManager", bus: MessageBus
    ) -> None:
        self._db_session = db_session
        self._engine_mgr = engine_mgr
        self._bus = bus
        self._websocket: WebSocket

        self._subscribe(EngineCreated, self._on_engine_created)
        self._subscribe(ResponseUserRequestMessage, self._on_engine_response_user_request)
        self._subscribe(ResponseStartedMessage, self._on_engine_response_started)
        self._subscribe(ResponseStoppedMessage, self._on_engine_response_stopped)
        self._subscribe(ResponseErrorMessage, self._on_engine_response_error)
        self._subscribe(ResponseStreamUpdateMessage, self._on_engine_response_stream)

    async def handle_connection(self, websocket: WebSocket) -> None:
        """Main connection handler for WebSocket connections."""
        try:
            self._websocket = websocket
            await self._websocket.accept()
            await self._handle_messages()
        except WebSocketDisconnect:
            pass
        except Exception as exc:
            error_message = WebSocketErrorMessage(name=type(exc).__name__, message=str(exc))
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
        return await self._engine_mgr.get_or_create(session_id, self._db_session)

    async def _send_message(self, message: WebSocketServerMessage) -> None:
        """Send a WebSocket message."""
        if self._websocket.client_state == WebSocketState.CONNECTED:
            await self._websocket.send_text(message.model_dump_json())
        else:
            _log.warning("Trying to send message while not connected")

    async def _on_engine_created(self, message: EngineCreated) -> None:
        await self._send_introduction_if_needed(message.session_id)

    async def _on_engine_response_user_request(self, message: ResponseUserRequestMessage) -> None:
        session_id = message.session_id
        await self._generate_response(self._engine_mgr.get(session_id))

    async def _on_engine_response_started(self, message: ResponseStartedMessage) -> None:
        session_id = message.session_id
        await self._send_message(WebSocketStatusMessage(session_id=session_id, status="started"))

    async def _on_engine_response_stopped(self, message: ResponseStoppedMessage) -> None:
        session_id = message.session_id
        await self._send_message(WebSocketStatusMessage(session_id=session_id, status="stopped"))

    async def _on_engine_response_error(self, message: ResponseErrorMessage) -> None:
        ws_msg = WebSocketErrorMessage.from_exception(message.session_id, message.error)
        await self._send_message(ws_msg)

    async def _on_engine_response_stream(self, message: ResponseStreamUpdateMessage) -> None:
        await self._send_message(WebSocketStreamMessage.from_stream_update(message))
