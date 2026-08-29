from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

import pytest
from pydantic import BaseModel
from sqlmodel.ext.asyncio.session import AsyncSession as AsyncDbSession

from llm_gamebook.db.crud.message import create_messages, get_message_count, get_messages
from llm_gamebook.db.crud.session import get_session, mark_session_ended, update_session_state
from llm_gamebook.db.models import Session
from llm_gamebook.db.models.message import Message, MessageKind
from llm_gamebook.engine.core_actions import CoreActionExecutor
from llm_gamebook.story import Project, StoryContext
from llm_gamebook.story.errors import CoreActionError, InvalidStepError, NoStateError
from llm_gamebook.story.state import (
    Action,
    EndGameAction,
    ForkAction,
    ResetGameAction,
    RestoreAction,
    SessionStateData,
)
from llm_gamebook.story.traits.graph import GraphTransitionAction


class DictPayload(BaseModel):
    data: dict[str, object] = {}


def _state(current_node_id: str) -> dict[str, object]:
    return {"entities": {"main": {"current_node_id": current_node_id}}}


def _seed_state_messages(session: Session, states: list[dict[str, object] | None]) -> list[Message]:
    base = datetime(2024, 1, 1, 12, 0, 0, tzinfo=UTC)
    return [
        Message(
            kind=MessageKind.RESPONSE,
            session_id=session.id,
            timestamp=base + timedelta(minutes=i),
            state=state,
        )
        for i, state in enumerate(states)
    ]


async def _seed(
    db_session: AsyncDbSession, session: Session, states: list[dict[str, object] | None]
) -> None:
    await create_messages(db_session, _seed_state_messages(session, states))


def _executor(
    session_id: UUID, project: Project, state: SessionStateData | None = None
) -> CoreActionExecutor:
    return CoreActionExecutor(session_id, StoryContext(project, state))


async def _get_session(db_session: AsyncDbSession, session_id: UUID) -> Session:
    result = await get_session(db_session, session_id)
    assert result is not None
    return result


async def test_restore_to_previous_step(
    db_session: AsyncDbSession, session: Session, project: Project
) -> None:
    await _seed(db_session, session, [_state("node_a"), None, _state("node_b")])
    executor = _executor(session.id, project, SessionStateData.model_validate(_state("node_b")))

    await executor.execute(db_session, RestoreAction(step=0))

    assert executor._context.store.get_state().get_field("main", "current_node_id") == "node_a"
    updated = await _get_session(db_session, session.id)
    assert updated.state == _state("node_a")


async def test_restore_to_latest(
    db_session: AsyncDbSession, session: Session, project: Project
) -> None:
    await _seed(db_session, session, [_state("node_a"), None, _state("node_b")])
    executor = _executor(session.id, project)

    await executor.execute(db_session, RestoreAction())

    assert executor._context.store.get_state().get_field("main", "current_node_id") == "node_b"
    updated = await _get_session(db_session, session.id)
    assert updated.state == _state("node_b")


async def test_restore_to_invalid_step(
    db_session: AsyncDbSession, session: Session, project: Project
) -> None:
    await _seed(db_session, session, [_state("node_a")])
    executor = _executor(session.id, project)

    with pytest.raises(InvalidStepError, match="greater than the current step"):
        await executor.execute(db_session, RestoreAction(step=5))

    with pytest.raises(InvalidStepError, match="Invalid step number"):
        await executor.execute(db_session, RestoreAction(step=-2))


async def test_restore_when_no_state_exists(
    db_session: AsyncDbSession, session: Session, project: Project
) -> None:
    await _seed(db_session, session, [None])
    executor = _executor(session.id, project)

    await executor.execute(db_session, RestoreAction(step=0))

    assert executor._context.store.get_state().is_empty()
    updated = await _get_session(db_session, session.id)
    assert updated.state is None


async def test_fork_from_historical_state(
    db_session: AsyncDbSession, session: Session, project: Project
) -> None:
    await _seed(db_session, session, [_state("node_a"), None, _state("node_b")])
    executor = _executor(session.id, project)

    result = await executor.execute(db_session, ForkAction(step=0))

    fork_id = result.new_session_id
    assert fork_id is not None
    assert fork_id != session.id
    fork = await _get_session(db_session, fork_id)
    assert fork.state == _state("node_a")
    assert fork.project_id == session.project_id
    assert fork.config_id == session.config_id
    assert fork.messages == []

    original = await _get_session(db_session, session.id)
    assert original.state is None
    assert await get_message_count(db_session, session.id) == 3


async def test_fork_from_latest(
    db_session: AsyncDbSession, session: Session, project: Project
) -> None:
    await _seed(db_session, session, [_state("node_a"), None, _state("node_b")])
    executor = _executor(session.id, project)

    result = await executor.execute(db_session, ForkAction())

    fork_id = result.new_session_id
    assert fork_id is not None
    fork = await _get_session(db_session, fork_id)
    assert fork.state == _state("node_b")


async def test_fork_is_independent(
    db_session: AsyncDbSession, session: Session, project: Project
) -> None:
    """Actions taken in a forked session do not affect the original session."""
    await _seed(db_session, session, [_state("node_a"), None, _state("node_b")])
    executor = _executor(session.id, project)

    result = await executor.execute(db_session, ForkAction(step=2))
    fork_id = result.new_session_id
    assert fork_id is not None

    # Take an action in the fork and persist its state
    fork_executor = _executor(fork_id, project, SessionStateData.model_validate(_state("node_b")))
    fork_executor._context.store.dispatch(
        GraphTransitionAction(entity_id="main", to="spark_of_hope")
    )
    await update_session_state(
        db_session, fork_id, fork_executor._context.store.get_state().data.model_dump()
    )

    original = await _get_session(db_session, session.id)
    assert original.state is None
    original_messages = await get_messages(db_session, session.id)
    assert original_messages[0].state == _state("node_a")

    fork = await get_session(db_session, fork_id)
    assert fork is not None
    assert fork.state == {"entities": {"main": {"current_node_id": "spark_of_hope"}}}


async def test_fork_when_no_state_exists(
    db_session: AsyncDbSession, session: Session, project: Project
) -> None:
    await _seed(db_session, session, [None])
    executor = _executor(session.id, project)

    with pytest.raises(NoStateError, match="No state found"):
        await executor.execute(db_session, ForkAction(step=0))


async def test_fork_to_invalid_step(
    db_session: AsyncDbSession, session: Session, project: Project
) -> None:
    await _seed(db_session, session, [_state("node_a")])
    executor = _executor(session.id, project)

    with pytest.raises(InvalidStepError, match="greater than the current step"):
        await executor.execute(db_session, ForkAction(step=1))


async def test_end_game_marks_session_ended(
    db_session: AsyncDbSession, session: Session, project: Project
) -> None:
    executor = _executor(session.id, project)

    await executor.execute(db_session, EndGameAction(reason="victory"))

    updated = await _get_session(db_session, session.id)
    assert updated.ended_at is not None


async def test_end_game_idempotent(
    db_session: AsyncDbSession, session: Session, project: Project
) -> None:
    executor = _executor(session.id, project)

    await executor.execute(db_session, EndGameAction(reason="victory"))
    ended = await _get_session(db_session, session.id)
    first_ended_at = ended.ended_at

    await executor.execute(db_session, EndGameAction(reason="again"))
    updated = await _get_session(db_session, session.id)

    assert updated.ended_at == first_ended_at


async def test_end_game_on_missing_session(db_session: AsyncDbSession, project: Project) -> None:
    executor = _executor(uuid4(), project)

    with pytest.raises(CoreActionError, match="not found"):
        await executor.execute(db_session, EndGameAction())


async def test_reset_game_clears_state(
    db_session: AsyncDbSession, session: Session, project: Project
) -> None:
    await _seed(db_session, session, [_state("node_a")])
    executor = _executor(session.id, project, SessionStateData.model_validate(_state("node_a")))
    await mark_session_ended(db_session, session.id)

    await executor.execute(db_session, ResetGameAction())

    assert executor._context.store.get_state().is_empty()
    updated = await _get_session(db_session, session.id)
    assert updated.state is None
    assert updated.ended_at is None


async def test_reset_game_on_already_reset_session(
    db_session: AsyncDbSession, session: Session, project: Project
) -> None:
    executor = _executor(session.id, project)

    await executor.execute(db_session, ResetGameAction())
    await executor.execute(db_session, ResetGameAction())

    assert executor._context.store.get_state().is_empty()
    updated = await _get_session(db_session, session.id)
    assert updated.state is None
    assert updated.ended_at is None


async def test_unknown_core_action(
    db_session: AsyncDbSession, session: Session, project: Project
) -> None:
    executor = _executor(session.id, project)

    action = Action[DictPayload](name="core/unknown", payload=DictPayload())
    with pytest.raises(CoreActionError, match="Unknown core action"):
        await executor.execute(db_session, action)
