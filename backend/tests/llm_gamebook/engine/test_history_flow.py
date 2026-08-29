"""Integration test for the full state history flow (restore, fork, end-game, reset)."""

from collections.abc import AsyncIterator
from datetime import UTC, datetime, timedelta

from pydantic_ai import ModelMessage
from pydantic_ai.models.function import AgentInfo, FunctionModel
from sqlmodel.ext.asyncio.session import AsyncSession as AsyncDbSession

from llm_gamebook.db.crud.message import create_messages, get_messages
from llm_gamebook.db.crud.session import get_session as get_session_crud
from llm_gamebook.db.models import Session
from llm_gamebook.db.models.message import Message, MessageKind
from llm_gamebook.engine.manager import EngineManager
from llm_gamebook.engine.message import ResponseErrorMessage
from llm_gamebook.message_bus import MessageBus
from llm_gamebook.story import Project, ProjectManager
from llm_gamebook.story.errors import SessionEndedError
from llm_gamebook.story.state import (
    EndGameAction,
    ForkAction,
    ResetGameAction,
    RestoreAction,
)


def _state(current_node_id: str) -> dict[str, object]:
    return {"entities": {"main": {"current_node_id": current_node_id}}}


async def _seed_history(db_session: AsyncDbSession, session: Session) -> None:
    """Seed a session with state history: node_a, gap, node_b."""
    base = datetime(2024, 1, 1, 12, 0, 0, tzinfo=UTC)
    states: list[dict[str, object] | None] = [_state("node_a"), None, _state("node_b")]
    messages = [
        Message(
            kind=MessageKind.RESPONSE,
            session_id=session.id,
            timestamp=base + timedelta(minutes=i),
            state=state,
        )
        for i, state in enumerate(states)
    ]
    await create_messages(db_session, messages)


async def test_full_history_flow(
    db_session: AsyncDbSession,
    session: Session,
    project: Project,
    project_manager: ProjectManager,
    message_bus: MessageBus,
    engine_manager: EngineManager,
) -> None:
    error_events: list[ResponseErrorMessage] = []
    message_bus.subscribe(ResponseErrorMessage, error_events.append)

    await _seed_history(db_session, session)

    # 1. Loading the session restores the latest state (node_b)
    engine = await engine_manager.get_or_create(session.id, db_session, project_manager)
    assert engine._context.session_state.get_field("main", "current_node_id") == "node_b"

    # 2. Restore to the first step (node_a)
    await engine.execute_core_action(db_session, RestoreAction(step=0))
    assert engine._context.session_state.get_field("main", "current_node_id") == "node_a"
    restored = await get_session_crud(db_session, session.id)
    assert restored is not None
    assert restored.state == _state("node_a")

    # 3. Reloading the session picks up the restored state
    _, reloaded_context = await engine_manager._create_model_and_context(
        session.id, db_session, project_manager
    )
    assert reloaded_context.session_state.get_field("main", "current_node_id") == "node_a"

    # 4. Fork from the latest historical state (node_b)
    fork_result = await engine.execute_core_action(db_session, ForkAction(step=2))
    fork_id = fork_result.new_session_id
    assert fork_id is not None
    fork = await get_session_crud(db_session, fork_id)
    assert fork is not None
    assert fork.state == _state("node_b")
    assert fork.messages == []

    # 5. The original session is unaffected by the fork
    original = await get_session_crud(db_session, session.id)
    assert original is not None
    assert original.state == _state("node_a")
    original_messages = await get_messages(db_session, session.id)
    assert len(original_messages) == 3
    assert original_messages[0].state == _state("node_a")
    assert original_messages[1].state is None
    assert original_messages[2].state == _state("node_b")

    # 6. End the game
    await engine.execute_core_action(db_session, EndGameAction(reason="victory"))
    ended = await get_session_crud(db_session, session.id)
    assert ended is not None
    assert ended.ended_at is not None

    # 7. No further responses are generated for an ended session
    count_before = await engine.session_adapter.get_message_count(db_session)
    await engine.generate_response(db_session)
    count_after = await engine.session_adapter.get_message_count(db_session)
    assert count_before == count_after == 3
    assert len(error_events) == 1
    assert isinstance(error_events[0].error, SessionEndedError)

    # 8. Reset the game: state is cleared and the session is playable again
    await engine.execute_core_action(db_session, ResetGameAction())
    reset = await get_session_crud(db_session, session.id)
    assert reset is not None
    assert reset.state is None
    assert reset.ended_at is None
    assert engine._context.session_state.is_empty()

    # Effective fields fall back to project defaults
    assert engine._context.get_field("main", "current_node_id") == "the_beginning"

    # No SessionEndedError is raised anymore
    async def stream_fn(messages: list[ModelMessage], info: AgentInfo) -> AsyncIterator[str]:
        yield "Response"

    engine.set_model(FunctionModel(stream_function=stream_fn))
    await engine.generate_response(db_session)
    assert not any(isinstance(e.error, SessionEndedError) for e in error_events[1:])
