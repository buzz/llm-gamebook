from contextlib import suppress
from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest
from fastapi import WebSocketDisconnect
from openai import APIError
from pydantic_ai import ModelResponse
from sqlmodel.ext.asyncio.session import AsyncSession as AsyncDbSession
from starlette.websockets import WebSocketDisconnect as StarletteDisconnect

from llm_gamebook.db.models.session import Session
from llm_gamebook.engine.manager import EngineManager
from llm_gamebook.engine.message import (
    EngineCreated,
    ResponseErrorMessage,
    ResponseStartedMessage,
    ResponseStoppedMessage,
    ResponseStreamUpdateMessage,
)
from llm_gamebook.web.schema.websocket.message import WebSocketPingMessage
from llm_gamebook.web.websocket.handler import WebSocketHandler


async def test_handle_connection_success(
    handler: WebSocketHandler, mock_websocket: AsyncMock
) -> None:
    mock_websocket.receive_text = AsyncMock(
        side_effect=WebSocketDisconnect(code=1000, reason="client disconnected")
    )

    with patch.object(handler, "close"):
        await handler.handle_connection(mock_websocket)

    mock_websocket.accept.assert_called_once()


async def test_handle_connection_disconnect(
    handler: WebSocketHandler, mock_websocket: AsyncMock
) -> None:
    mock_websocket.receive_text = AsyncMock(
        side_effect=WebSocketDisconnect(code=1000, reason="client disconnected")
    )

    with patch.object(handler, "close"):
        await handler.handle_connection(mock_websocket)

    mock_websocket.accept.assert_called_once()


async def test_handle_connection_error(
    handler: WebSocketHandler, mock_websocket: AsyncMock
) -> None:
    error = ValueError("Test error")
    mock_websocket.receive_text = AsyncMock(side_effect=error)

    with patch.object(handler, "close"), pytest.raises(ValueError, match="Test error"):
        await handler.handle_connection(mock_websocket)

    mock_websocket.send_text.assert_called_once()
    call_args = mock_websocket.send_text.call_args[0][0]
    assert '"name":"ValueError"' in call_args
    assert '"message":"Test error"' in call_args


async def test_send_introduction_if_needed_new_session(
    handler: WebSocketHandler,
    mock_websocket: AsyncMock,
    session: Session,
    engine_manager: EngineManager,
    db_session: AsyncDbSession,
) -> None:
    handler._websocket = mock_websocket

    await engine_manager.get_or_create(session.id, db_session)


async def test_send_introduction_if_needed_existing_session(
    handler: WebSocketHandler,
    mock_websocket: AsyncMock,
    session: Session,
    engine_manager: EngineManager,
    db_session: AsyncDbSession,
) -> None:
    handler._websocket = mock_websocket

    await engine_manager.get_or_create(session.id, db_session)


async def test_handle_messages_ping(handler: WebSocketHandler, mock_websocket: AsyncMock) -> None:
    mock_websocket.receive_text = AsyncMock(
        side_effect=[
            WebSocketPingMessage(kind="ping").model_dump_json(),
            StarletteDisconnect(code=1000),
        ]
    )
    handler._websocket = mock_websocket

    with suppress(StarletteDisconnect):
        await handler._handle_messages()

    mock_websocket.send_text.assert_called_once()
    call_args = mock_websocket.send_text.call_args[0][0]
    assert '"kind":"pong"' in call_args


async def test_handle_messages_invalid_json(
    handler: WebSocketHandler, mock_websocket: AsyncMock
) -> None:
    mock_websocket.receive_text = AsyncMock(
        side_effect=[
            "invalid json {{{",
            WebSocketDisconnect(code=1000),
        ]
    )
    handler._websocket = mock_websocket

    with suppress(WebSocketDisconnect):
        await handler._handle_messages()

    mock_websocket.send_text.assert_not_called()


async def test_generate_response_success(
    handler: WebSocketHandler,
    mock_websocket: AsyncMock,
    session: Session,
    engine_manager: EngineManager,
    db_session: AsyncDbSession,
) -> None:
    handler._websocket = mock_websocket

    engine = await engine_manager.get_or_create(session.id, db_session)

    with patch.object(engine, "generate_response", new_callable=AsyncMock):
        await handler._generate_response(engine)


async def test_generate_response_api_error(
    handler: WebSocketHandler,
    mock_websocket: AsyncMock,
    session: Session,
    engine_manager: EngineManager,
    db_session: AsyncDbSession,
) -> None:
    handler._websocket = mock_websocket

    engine = await engine_manager.get_or_create(session.id, db_session)

    with patch.object(
        engine,
        "generate_response",
        side_effect=APIError(message="API Error", body=None, request=None),  # type: ignore[arg-type]
    ):
        await handler._generate_response(engine)

    mock_websocket.send_text.assert_called_once()
    call_args = mock_websocket.send_text.call_args[0][0]
    assert '"name":"APIError"' in call_args
    assert '"message":"API Error"' in call_args


async def test_on_engine_created(
    handler: WebSocketHandler,
    mock_websocket: AsyncMock,
    session: Session,
    engine_manager: EngineManager,
    db_session: AsyncDbSession,
) -> None:
    handler._websocket = mock_websocket

    await engine_manager.get_or_create(session.id, db_session)
    engine = engine_manager.get(session.id)

    with patch.object(engine, "generate_response", new_callable=AsyncMock):
        message = EngineCreated(session_id=session.id)
        await handler._on_engine_created(message)


async def test_on_engine_response_started(
    handler: WebSocketHandler, mock_websocket: AsyncMock, session: Session
) -> None:
    handler._websocket = mock_websocket

    message = ResponseStartedMessage(session_id=session.id)
    await handler._on_engine_response_started(message)

    mock_websocket.send_text.assert_called_once()
    call_args = mock_websocket.send_text.call_args[0][0]
    assert '"kind":"status"' in call_args
    assert '"status":"started"' in call_args
    assert f'"{session.id}"' in call_args


async def test_on_engine_response_stopped(
    handler: WebSocketHandler, mock_websocket: AsyncMock, session: Session
) -> None:
    handler._websocket = mock_websocket

    message = ResponseStoppedMessage(session_id=session.id)
    await handler._on_engine_response_stopped(message)

    mock_websocket.send_text.assert_called_once()
    call_args = mock_websocket.send_text.call_args[0][0]
    assert '"kind":"status"' in call_args
    assert '"status":"stopped"' in call_args
    assert f'"{session.id}"' in call_args


async def test_on_engine_response_error(
    handler: WebSocketHandler, mock_websocket: AsyncMock, session: Session
) -> None:
    handler._websocket = mock_websocket

    error = ValueError("Test error")
    message = ResponseErrorMessage(session_id=session.id, error=error)
    await handler._on_engine_response_error(message)

    mock_websocket.send_text.assert_called_once()
    call_args = mock_websocket.send_text.call_args[0][0]
    assert '"kind":"error"' in call_args
    assert '"name":"ValueError"' in call_args
    assert '"message":"Test error"' in call_args


async def test_on_engine_response_stream(
    handler: WebSocketHandler, mock_websocket: AsyncMock, session: Session
) -> None:
    handler._websocket = mock_websocket

    model_response = ModelResponse(
        parts=[],
        model_name="test",
        finish_reason="stop",
    )
    message = ResponseStreamUpdateMessage(
        session_id=session.id,
        response=model_response,
        response_id=uuid4(),
        part_ids=[],
    )
    await handler._on_engine_response_stream(message)

    mock_websocket.send_text.assert_called_once()
    call_args = mock_websocket.send_text.call_args[0][0]
    assert '"kind":"stream"' in call_args
    assert f'"{session.id}"' in call_args
