from pydantic_ai import ModelResponse, TextPart, ToolCallPart
from sqlmodel.ext.asyncio.session import AsyncSession as AsyncDbSession

from llm_gamebook.engine.engine import StoryEngine

from .mocks.model import MockModel
from .mocks.player import MockPlayer


async def test_story_flow(
    test_model: MockModel,
    test_player: MockPlayer,
    story_engine: StoryEngine,
    db_session: AsyncDbSession,
) -> None:
    # Bedroom
    test_model.add_responses(
        lambda _, info: len(info.function_tools) == 0,  # No tool calls on introduction
        ModelResponse([TextPart("Introduction")]),
    )
    await story_engine.generate_response(db_session, streaming=False)

    system_prompt = test_model.current_system_prompt
    assert "You are the narrator of a branching interactive story." in system_prompt
    assert "Current node: Bedroom (bedroom)" in system_prompt
    assert "dark, dim light" in system_prompt
    assert "cockroaches under bed" in system_prompt
    assert "A leaflet was placed under" not in system_prompt

    # Living room: triggers location transition
    await test_player.send_text("go to living room", db_session)
    test_model.add_responses(
        ModelResponse(parts=[ToolCallPart("change_location", {"to": "living_room"})]),
        lambda msgs, _: msgs[-1].parts[0].part_kind == "tool-return",
        ModelResponse(parts=[TextPart("You are in the living room now…")]),
    )
    await story_engine.generate_response(db_session, streaming=False)

    system_prompt = test_model.current_system_prompt
    assert "run-down living room" in system_prompt
    assert "messy, scattered with empty bottles" in system_prompt
    assert "A leaflet was placed under" in system_prompt

    # Take leaflet: triggers The Meeting story arc transition
    await test_player.send_text("take the leaflet", db_session)
    test_model.add_responses(
        ModelResponse(parts=[ToolCallPart("progress_the_meeting_story", {"to": "leaflet_found"})]),
        lambda msgs, _: msgs[-1].parts[0].part_kind == "tool-return",
        ModelResponse(parts=[TextPart("You pick up the leaflet…")]),
    )
    await story_engine.generate_response(db_session, streaming=False)

    system_prompt = test_model.current_system_prompt
    assert "A leaflet was placed under" not in system_prompt
    assert "Player found the leaflet" in system_prompt
