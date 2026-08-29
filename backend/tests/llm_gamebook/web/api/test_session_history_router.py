"""Endpoint tests for the session state-history API (restore, fork, end-game, reset, states)."""

from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

from fastapi.testclient import TestClient
from sqlmodel.ext.asyncio.session import AsyncSession as AsyncDbSession

from llm_gamebook.db.crud.message import create_messages, get_message_count
from llm_gamebook.db.crud.session import mark_session_ended, update_session_state
from llm_gamebook.db.models import Message, Session
from llm_gamebook.db.models.message import MessageKind


def _state(value: str) -> dict[str, object]:
    return {"entities": {"main": {"current_node_id": value}}}


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
    """Persist response messages with the given per-step states (None = gap)."""
    await create_messages(db_session, _seed_state_messages(session, states))


async def _get(db_session: AsyncDbSession, session_id: UUID) -> Session:
    # populate_existing: refresh attributes that the app's DB session may have changed
    session = await db_session.get(Session, session_id, populate_existing=True)
    assert session is not None
    return session


# Snapshots at steps 2, 5, and 7 with gaps in between.
GAPPED_STATES: list[dict[str, object] | None] = [
    None,
    None,
    _state("a"),
    None,
    None,
    _state("b"),
    None,
    _state("c"),
]


async def test_restore_specific_step_with_gaps(
    client: TestClient, db_session: AsyncDbSession, session: Session
) -> None:
    """Restoring step 4 picks the snapshot at step 2; later messages remain."""
    await _seed(db_session, session, GAPPED_STATES)

    response = client.post(f"/api/sessions/{session.id}/restore", json={"step": 4})

    assert response.status_code == 200
    assert (await _get(db_session, session.id)).state == _state("a")
    assert await get_message_count(db_session, session.id) == 8


async def test_restore_latest(
    client: TestClient, db_session: AsyncDbSession, session: Session
) -> None:
    await _seed(db_session, session, GAPPED_STATES)

    response = client.post(f"/api/sessions/{session.id}/restore", json={"step": -1})

    assert response.status_code == 200
    assert (await _get(db_session, session.id)).state == _state("c")


async def test_restore_no_snapshots(
    client: TestClient, db_session: AsyncDbSession, session: Session
) -> None:
    """Restoring a stateless session ends up with the empty (default) state."""
    await _seed(db_session, session, [None, None])

    response = client.post(f"/api/sessions/{session.id}/restore", json={"step": 0})

    assert response.status_code == 200
    assert (await _get(db_session, session.id)).state is None


async def test_restore_invalid_step(
    client: TestClient, db_session: AsyncDbSession, session: Session
) -> None:
    await _seed(db_session, session, [None, None, None, None, None, None])

    too_high = client.post(f"/api/sessions/{session.id}/restore", json={"step": 6})
    too_low = client.post(f"/api/sessions/{session.id}/restore", json={"step": -2})

    assert too_high.status_code == 422
    assert too_low.status_code == 422


async def test_restore_nonexistent_session(client: TestClient) -> None:
    response = client.post(f"/api/sessions/{uuid4()}/restore", json={"step": -1})

    assert response.status_code == 404


async def test_restore_ended_session_stays_ended(
    client: TestClient, db_session: AsyncDbSession, session: Session
) -> None:
    """Restore is soft time-travel: it does not un-end an ended session."""
    await _seed(db_session, session, GAPPED_STATES)
    await mark_session_ended(db_session, session.id)

    response = client.post(f"/api/sessions/{session.id}/restore", json={"step": 4})

    assert response.status_code == 200
    updated = await _get(db_session, session.id)
    assert updated.state == _state("a")
    assert updated.ended_at is not None


async def test_fork_from_historical_step(
    client: TestClient, db_session: AsyncDbSession, session: Session
) -> None:
    """Fork step 4 forks the step-2 snapshot into a new, message-less session."""
    await _seed(db_session, session, GAPPED_STATES)
    await update_session_state(db_session, session.id, _state("c"))

    response = client.post(f"/api/sessions/{session.id}/fork", json={"step": 4})

    assert response.status_code == 201
    data = response.json()
    new_id = data["id"]
    assert new_id != str(session.id)
    assert data["projectId"] == session.project_id
    assert data["configId"] == str(session.config_id)
    assert data["messages"] == []

    fork = await _get(db_session, UUID(new_id))
    assert fork.state == _state("a")

    source = await _get(db_session, session.id)
    assert source.state == _state("c")
    assert source.ended_at is None
    assert await get_message_count(db_session, session.id) == 8


async def test_fork_from_latest(
    client: TestClient, db_session: AsyncDbSession, session: Session
) -> None:
    await _seed(db_session, session, GAPPED_STATES)

    response = client.post(f"/api/sessions/{session.id}/fork", json={"step": -1})

    assert response.status_code == 201
    fork = await _get(db_session, UUID(response.json()["id"]))
    assert fork.state == _state("c")


async def test_fork_no_state(
    client: TestClient, db_session: AsyncDbSession, session: Session
) -> None:
    await _seed(db_session, session, [None])

    response = client.post(f"/api/sessions/{session.id}/fork", json={"step": -1})

    assert response.status_code == 409


async def test_fork_invalid_step(
    client: TestClient, db_session: AsyncDbSession, session: Session
) -> None:
    await _seed(db_session, session, [None, None, None, None, None, None])

    too_high = client.post(f"/api/sessions/{session.id}/fork", json={"step": 6})
    too_low = client.post(f"/api/sessions/{session.id}/fork", json={"step": -2})

    assert too_high.status_code == 422
    assert too_low.status_code == 422


async def test_end_game_active_session(
    client: TestClient, db_session: AsyncDbSession, session: Session
) -> None:
    response = client.post(f"/api/sessions/{session.id}/end-game")

    assert response.status_code == 200
    assert (await _get(db_session, session.id)).ended_at is not None


async def test_end_game_idempotent(
    client: TestClient, db_session: AsyncDbSession, session: Session
) -> None:
    first = client.post(f"/api/sessions/{session.id}/end-game")
    ended_at = (await _get(db_session, session.id)).ended_at
    assert first.status_code == 200
    assert ended_at is not None

    second = client.post(f"/api/sessions/{session.id}/end-game", json={"reason": "again"})

    assert second.status_code == 200
    assert (await _get(db_session, session.id)).ended_at == ended_at


async def test_end_game_with_reason(
    client: TestClient, db_session: AsyncDbSession, session: Session
) -> None:
    response = client.post(
        f"/api/sessions/{session.id}/end-game", json={"reason": "reached the ending"}
    )

    assert response.status_code == 200
    assert (await _get(db_session, session.id)).ended_at is not None


async def test_reset_active_session(
    client: TestClient, db_session: AsyncDbSession, session: Session
) -> None:
    """Reset clears the state but preserves the message history."""
    await _seed(db_session, session, [_state("a"), _state("b")])
    await update_session_state(db_session, session.id, _state("b"))

    response = client.post(f"/api/sessions/{session.id}/reset")

    assert response.status_code == 200
    updated = await _get(db_session, session.id)
    assert updated.state is None
    assert await get_message_count(db_session, session.id) == 2


async def test_reset_ended_session(
    client: TestClient, db_session: AsyncDbSession, session: Session
) -> None:
    """Reset un-ends an ended session, making it playable again."""
    await _seed(db_session, session, [_state("a")])
    await update_session_state(db_session, session.id, _state("a"))
    await mark_session_ended(db_session, session.id)

    response = client.post(f"/api/sessions/{session.id}/reset")

    assert response.status_code == 200
    updated = await _get(db_session, session.id)
    assert updated.state is None
    assert updated.ended_at is None


async def test_get_states(client: TestClient, db_session: AsyncDbSession, session: Session) -> None:
    """Snapshots are listed in ascending step order with timestamp and field count."""
    await _seed(db_session, session, GAPPED_STATES)

    response = client.get(f"/api/sessions/{session.id}/states")

    assert response.status_code == 200
    data = response.json()["data"]
    assert [entry["step"] for entry in data] == [2, 5, 7]
    assert [entry["fieldCount"] for entry in data] == [1, 1, 1]
    timestamps = [entry["timestamp"] for entry in data]
    assert all(ts is not None for ts in timestamps)
    assert timestamps == sorted(timestamps)


async def test_get_states_empty(
    client: TestClient, db_session: AsyncDbSession, session: Session
) -> None:
    response = client.get(f"/api/sessions/{session.id}/states")

    assert response.status_code == 200
    assert response.json()["data"] == []


async def test_get_states_nonexistent_session(client: TestClient) -> None:
    response = client.get(f"/api/sessions/{uuid4()}/states")

    assert response.status_code == 404
