"""End-to-end state-history flow against a real (mocked-LLM) broken-bulb session.

Plays turns with the mock model, letting the runner store real state
snapshots in the message history, then exercises the core actions
(restore/undo, continue-after-restore, fork, end-game, reset) against that
generated history.

Note: state snapshots only contain explicitly-set fields, so the first
snapshot appears on the first tool-call turn (the introduction stores no
state). Restoring to a step before the first snapshot yields the default
state, which ``get_field`` resolves from the project definition.
"""

from uuid import UUID

from pydantic_ai import ModelResponse, TextPart, ToolCallPart
from sqlmodel.ext.asyncio.session import AsyncSession as AsyncDbSession

from llm_gamebook.db.crud.message import find_previous_state, get_message_count, get_state_snapshots
from llm_gamebook.db.crud.session import get_session
from llm_gamebook.engine.engine import StoryEngine
from llm_gamebook.engine.manager import EngineManager
from llm_gamebook.story.project_manager import ProjectManager
from llm_gamebook.story.state import EndGameAction, ForkAction, ResetGameAction, RestoreAction

from .mocks.model import MockModel
from .mocks.player import MockPlayer


async def _respond_with_location(test_model: MockModel, location: str, text: str) -> None:
    """Queue a mock model turn that moves the player to the given location."""
    test_model.add_responses(
        ModelResponse(parts=[ToolCallPart("change_location", {"to": location})]),
        lambda msgs, _: msgs[-1].parts[0].part_kind == "tool-return",
        ModelResponse(parts=[TextPart(text)]),
    )


async def _play_intro(
    test_model: MockModel, story_engine: StoryEngine, db_session: AsyncDbSession
) -> None:
    test_model.add_responses(
        lambda _, info: len(info.function_tools) == 0,  # No tool calls on introduction
        ModelResponse([TextPart("Introduction")]),
    )
    await story_engine.generate_response(db_session)


async def _play_three_turns(
    test_model: MockModel, story_engine: StoryEngine, db_session: AsyncDbSession
) -> None:
    """Introduction, then living room, then bathroom (stores real snapshots)."""
    player = MockPlayer(story_engine)
    await _play_intro(test_model, story_engine, db_session)

    await player.send_text("go to living room", db_session)
    await _respond_with_location(test_model, "living_room", "You are in the living room.")
    await story_engine.generate_response(db_session)

    await player.send_text("go to the bathroom", db_session)
    await _respond_with_location(test_model, "bathroom", "You are in the bathroom.")
    await story_engine.generate_response(db_session)


async def _end_and_reset(
    story_engine: StoryEngine,
    fork_engine: StoryEngine,
    session_id: UUID,
    fork_id: UUID,
    db_session: AsyncDbSession,
) -> None:
    """End the original game (restore still works), then reset the fork."""
    await story_engine.execute_core_action(db_session, EndGameAction(reason="smoke test"))
    original = await get_session(db_session, session_id)
    assert original is not None
    assert original.ended_at is not None

    # Restore works on an ended session, but it stays ended.
    await story_engine.execute_core_action(db_session, RestoreAction(step=-1))
    original = await get_session(db_session, session_id)
    assert original is not None
    assert original.ended_at is not None
    assert story_engine._context.get_field("locations", "current_node_id") == "in_the_street"

    await fork_engine.execute_core_action(db_session, EndGameAction())
    fork = await get_session(db_session, fork_id)
    assert fork is not None
    assert fork.ended_at is not None

    await fork_engine.execute_core_action(db_session, ResetGameAction())
    fork = await get_session(db_session, fork_id)
    assert fork is not None
    assert fork.state is None
    assert fork.ended_at is None


async def test_state_history_flow(
    test_model: MockModel,
    story_engine: StoryEngine,
    engine_manager: EngineManager,
    project_manager: ProjectManager,
    db_session: AsyncDbSession,
) -> None:
    session_id = story_engine.session_adapter.session_id

    await _play_three_turns(test_model, story_engine, db_session)
    assert story_engine._context.get_field("locations", "current_node_id") == "bathroom"

    # Snapshots were stored in the message history during play.
    # (The introduction stores no state; snapshot counts depend on prior state.)
    snapshots = await get_state_snapshots(db_session, session_id)
    assert len(snapshots) >= 2
    assert [s.step for s in snapshots] == sorted(s.step for s in snapshots)
    assert all(s.field_count > 0 for s in snapshots)
    first_state = await find_previous_state(db_session, session_id, snapshots[0].step)
    assert first_state == {"entities": {"locations": {"current_node_id": "living_room"}}}
    message_count = await get_message_count(db_session, session_id)

    # Undo: restore the first snapshot (living room).
    first_step = snapshots[0].step
    await story_engine.execute_core_action(db_session, RestoreAction(step=first_step))
    assert story_engine._context.get_field("locations", "current_node_id") == "living_room"
    updated = await get_session(db_session, session_id)
    assert updated is not None
    assert updated.state == await find_previous_state(db_session, session_id, first_step)
    # Soft time-travel: messages after the restore point are preserved.
    assert await get_message_count(db_session, session_id) == message_count

    # Continue playing after the restore: new snapshots append on top.
    await MockPlayer(story_engine).send_text("go outside", db_session)
    await _respond_with_location(test_model, "in_the_street", "You are on the street.")
    await story_engine.generate_response(db_session)
    assert story_engine._context.get_field("locations", "current_node_id") == "in_the_street"
    continued = await get_state_snapshots(db_session, session_id)
    assert len(continued) > len(snapshots)
    assert [s.step for s in continued] == sorted(s.step for s in continued)
    assert continued[-1].step > snapshots[-1].step

    # Fork from the latest state; the fork starts on the street.
    result = await story_engine.execute_core_action(db_session, ForkAction(step=-1))
    fork_id = result.new_session_id
    assert fork_id is not None
    original = await get_session(db_session, session_id)
    fork = await get_session(db_session, fork_id)
    assert original is not None
    assert fork is not None
    assert fork.project_id == original.project_id
    assert fork.config_id == original.config_id
    assert fork.messages == []
    assert fork.state == original.state

    # A fresh engine for the fork (the production path for idle sessions)
    # loads the forked state from the database.
    fork_engine = await engine_manager.get_or_create(fork_id, db_session, project_manager)
    assert fork_engine._context.get_field("locations", "current_node_id") == "in_the_street"
    assert await get_message_count(db_session, session_id) == message_count + 3

    await _end_and_reset(story_engine, fork_engine, session_id, fork_id, db_session)


async def test_restore_before_first_snapshot_yields_default_state(
    test_model: MockModel,
    story_engine: StoryEngine,
    db_session: AsyncDbSession,
) -> None:
    session_id = story_engine.session_adapter.session_id

    await _play_intro(test_model, story_engine, db_session)
    await MockPlayer(story_engine).send_text("go to living room", db_session)
    await _respond_with_location(test_model, "living_room", "You are in the living room.")
    await story_engine.generate_response(db_session)

    snapshots = await get_state_snapshots(db_session, session_id)
    assert len(snapshots) == 1

    # Restore to a step before the first stored snapshot: state goes empty.
    await story_engine.execute_core_action(db_session, RestoreAction(step=snapshots[0].step - 1))

    session = await get_session(db_session, session_id)
    assert session is not None
    assert session.state is None
    # Unset fields fall back to the project definition defaults.
    assert story_engine._context.get_field("locations", "current_node_id") == "bedroom"
