"""Integration tests: ActionDispatched events are delivered over the WebSocket."""

import asyncio
from datetime import UTC, datetime
from json import loads
from typing import TYPE_CHECKING
from unittest.mock import AsyncMock

from fastapi import WebSocket
from pydantic_ai import ModelResponse, TextPart, ToolCallPart
from sqlmodel.ext.asyncio.session import AsyncSession as AsyncDbSession
from starlette.websockets import WebSocketState

from llm_gamebook.db.models import Session
from llm_gamebook.engine.manager import EngineManager
from llm_gamebook.engine.message import ResponseStoppedMessage
from llm_gamebook.message_bus import MessageBus
from llm_gamebook.story.project_manager import ProjectManager
from llm_gamebook.web.websocket.handler import WebSocketHandler

from .mocks.model import MockModel
from .mocks.player import MockPlayer

if TYPE_CHECKING:
    from llm_gamebook.engine.engine import StoryEngine


async def test_action_dispatched_delivered_over_websocket(
    engine_manager: EngineManager,
    session: Session,
    db_session: AsyncDbSession,
    project_manager: ProjectManager,
    message_bus: MessageBus,
    test_model: MockModel,
) -> None:
    """An action dispatched during an agent step reaches the connected WebSocket client."""
    mock_websocket = AsyncMock(spec=WebSocket)
    mock_websocket.client_state = WebSocketState.CONNECTED
    mock_websocket.send_text = AsyncMock()

    engine: StoryEngine = await engine_manager.get_or_create(
        session.id, db_session, project_manager
    )
    engine.set_model(test_model)

    # Connect the handler after engine creation, so the introduction is driven
    # directly below instead of by the handler's EngineCreated subscription.
    handler = WebSocketHandler(db_session, engine_manager, message_bus)
    handler._websocket = mock_websocket

    stopped = asyncio.Event()
    stop_count = 0

    def on_response_stopped(message: ResponseStoppedMessage) -> None:
        nonlocal stop_count
        stop_count += 1
        if stop_count >= 2:
            stopped.set()

    message_bus.subscribe(ResponseStoppedMessage, on_response_stopped)

    # Introduction step (no tools available yet)
    test_model.add_responses(
        lambda _, info: len(info.function_tools) == 0,
        ModelResponse([TextPart("Introduction")]),
    )
    await engine.generate_response(db_session)

    # Agent step: the user request publishes ResponseUserRequestMessage, which
    # the handler turns into a response generation. The model calls the
    # change_location tool, which dispatches graph/transition.
    player = MockPlayer(engine)
    await player.send_text("go to living room", db_session)
    test_model.add_responses(
        ModelResponse(parts=[ToolCallPart("change_location", {"to": "living_room"})]),
        lambda msgs, _: msgs[-1].parts[0].part_kind == "tool-return",
        ModelResponse(parts=[TextPart("You are in the living room now…")]),
    )

    await asyncio.wait_for(stopped.wait(), timeout=10)
    await message_bus.wait_all()
    handler.close()

    sent = [loads(c.args[0]) for c in mock_websocket.send_text.call_args_list]
    actions = [m for m in sent if m.get("kind") == "action_dispatched"]
    assert len(actions) == 1

    message = actions[0]
    assert message["kind"] == "action_dispatched"
    assert message["sessionId"] == str(session.id)
    assert message["actionType"] == "graph/transition"
    assert message["payload"] == {"entity_id": "locations", "to": "living_room"}
    parsed = datetime.fromisoformat(message["timestamp"])
    assert parsed == parsed.astimezone(UTC)
