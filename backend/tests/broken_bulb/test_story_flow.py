from collections import Counter
from uuid import UUID

from pydantic_ai import ModelResponse, TextPart, ToolCallPart
from sqlmodel.ext.asyncio.session import AsyncSession as AsyncDbSession

from llm_gamebook.db.crud.message import get_messages
from llm_gamebook.db.models.message import MessageKind
from llm_gamebook.db.models.part import PartKind
from llm_gamebook.engine.engine import StoryEngine

from .mocks.model import MockModel
from .mocks.player import MockPlayer


async def assert_no_duplicate_user_prompts(session_id: UUID, db_session: AsyncDbSession) -> None:
    messages = await get_messages(db_session, session_id)
    user_prompts = [
        part.content
        for msg in messages
        if msg.kind == MessageKind.REQUEST
        for part in msg.parts
        if part.kind == PartKind.USER_PROMPT and part.content
    ]
    duplicates = [p for p, count in Counter(user_prompts).items() if count > 1]
    assert not duplicates, f"Duplicate user prompts found: {duplicates}"


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
    await story_engine.generate_response(db_session)

    system_prompt = test_model.current_system_prompt
    assert "You are the narrator of a branching interactive story." in system_prompt
    assert "Current node: Bedroom (bedroom)" in system_prompt
    assert "dark, dim light" in system_prompt
    assert "cockroaches under bed" in system_prompt
    assert "A leaflet was placed under" not in system_prompt

    message_count = await story_engine.session_adapter.get_message_count(db_session)
    assert message_count == 2
    await assert_no_duplicate_user_prompts(story_engine.session_adapter.session_id, db_session)

    # Living room: triggers location transition
    await test_player.send_text("go to living room", db_session)
    test_model.add_responses(
        ModelResponse(parts=[ToolCallPart("change_location", {"to": "living_room"})]),
        lambda msgs, _: msgs[-1].parts[0].part_kind == "tool-return",
        ModelResponse(parts=[TextPart("You are in the living room now…")]),
    )
    await story_engine.generate_response(db_session)

    system_prompt = test_model.current_system_prompt
    assert "run-down living room" in system_prompt
    assert "messy, scattered with empty bottles" in system_prompt
    assert "A leaflet was placed under" in system_prompt

    message_count = await story_engine.session_adapter.get_message_count(db_session)
    assert message_count == 5
    await assert_no_duplicate_user_prompts(story_engine.session_adapter.session_id, db_session)

    # Take leaflet: triggers The Meeting story arc transition
    await test_player.send_text("take the leaflet", db_session)
    test_model.add_responses(
        ModelResponse(parts=[ToolCallPart("progress_the_meeting_story", {"to": "leaflet_found"})]),
        lambda msgs, _: msgs[-1].parts[0].part_kind == "tool-return",
        ModelResponse(parts=[TextPart("You pick up the leaflet…")]),
    )
    await story_engine.generate_response(db_session)

    system_prompt = test_model.current_system_prompt
    assert "A leaflet was placed under" not in system_prompt
    assert "Player found the leaflet" in system_prompt

    message_count = await story_engine.session_adapter.get_message_count(db_session)
    assert message_count == 8
    await assert_no_duplicate_user_prompts(story_engine.session_adapter.session_id, db_session)
