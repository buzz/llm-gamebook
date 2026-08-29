"""Integration tests for the message bus bridge (stage 6)."""

from typing import TYPE_CHECKING

from pydantic_ai import ModelResponse, TextPart, ToolCallPart
from sqlmodel.ext.asyncio.session import AsyncSession as AsyncDbSession

from llm_gamebook.db.models import Session
from llm_gamebook.engine.manager import EngineManager
from llm_gamebook.message_bus import MessageBus
from llm_gamebook.story.project_manager import ProjectManager
from llm_gamebook.story.state import ActionDispatched

from .mocks.model import MockModel
from .mocks.player import MockPlayer

if TYPE_CHECKING:
    from llm_gamebook.engine.engine import StoryEngine


async def test_engine_dispatch_publishes_action_dispatched(
    engine_manager: EngineManager,
    session: Session,
    db_session: AsyncDbSession,
    project_manager: ProjectManager,
    message_bus: MessageBus,
    test_model: MockModel,
) -> None:
    """Actions dispatched during an agent step are observable on the application bus."""
    engine: StoryEngine = await engine_manager.get_or_create(
        session.id, db_session, project_manager
    )
    engine.set_model(test_model)
    player = MockPlayer(engine)

    received: list[ActionDispatched] = []
    message_bus.subscribe(ActionDispatched, received.append)

    # Introduction step (no tools available yet)
    test_model.add_responses(
        lambda _, info: len(info.function_tools) == 0,
        ModelResponse([TextPart("Introduction")]),
    )
    await engine.generate_response(db_session)
    assert received == []

    # Agent step: model calls the change_location tool, which dispatches graph/transition
    await player.send_text("go to living room", db_session)
    test_model.add_responses(
        ModelResponse(parts=[ToolCallPart("change_location", {"to": "living_room"})]),
        lambda msgs, _: msgs[-1].parts[0].part_kind == "tool-return",
        ModelResponse(parts=[TextPart("You are in the living room now…")]),
    )
    await engine.generate_response(db_session)

    assert len(received) == 1
    message = received[0]
    assert message.session_id == session.id
    assert message.action_type == "graph/transition"
    assert message.payload == {"entity_id": "locations", "to": "living_room"}
    assert message.timestamp.tzinfo is not None

    # The reducer applied the transition to the session state
    assert engine._context.session_state.get_field("locations", "current_node_id") == "living_room"
