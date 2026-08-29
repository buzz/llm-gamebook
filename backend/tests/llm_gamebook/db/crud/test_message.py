from datetime import UTC, datetime, timedelta

import pytest
from sqlmodel.ext.asyncio.session import AsyncSession as AsyncDbSession

from llm_gamebook.db.crud import message as message_crud
from llm_gamebook.db.models import Message, Session
from llm_gamebook.db.models.message import MessageKind


async def test_get_message_count(db_session: AsyncDbSession, session: Session) -> None:
    """Test counting messages for a session."""
    msg1 = Message(
        kind=MessageKind.REQUEST,
        session_id=session.id,
        timestamp=datetime.now(UTC),
    )
    msg2 = Message(
        kind=MessageKind.RESPONSE,
        session_id=session.id,
        timestamp=datetime.now(UTC),
    )

    await message_crud.create_message(db_session, msg1)
    await message_crud.create_message(db_session, msg2)

    count = await message_crud.get_message_count(db_session, session.id)

    assert count == 2


async def test_get_message_count_empty(db_session: AsyncDbSession, session: Session) -> None:
    """Test counting messages when session has no messages."""
    count = await message_crud.get_message_count(db_session, session.id)

    assert count == 0


async def test_get_messages(db_session: AsyncDbSession, session: Session) -> None:
    """Test retrieving messages for a session with ordering."""
    timestamp_earlier = datetime(2024, 1, 1, 12, 0, 0, tzinfo=UTC)
    timestamp_later = datetime(2024, 1, 1, 12, 1, 0, tzinfo=UTC)

    msg1 = Message(
        kind=MessageKind.REQUEST,
        session_id=session.id,
        timestamp=timestamp_earlier,
    )
    msg2 = Message(
        kind=MessageKind.RESPONSE,
        session_id=session.id,
        timestamp=timestamp_later,
    )

    await message_crud.create_message(db_session, msg1)
    await message_crud.create_message(db_session, msg2)

    messages = await message_crud.get_messages(db_session, session.id)

    assert len(messages) == 2
    assert messages[0].id == msg1.id
    assert messages[1].id == msg2.id


async def test_get_messages_empty(db_session: AsyncDbSession, session: Session) -> None:
    """Test retrieving messages when session has no messages."""
    messages = await message_crud.get_messages(db_session, session.id)

    assert messages == []


async def test_create_message(db_session: AsyncDbSession, session: Session) -> None:
    """Test creating a single message."""
    msg = Message(kind=MessageKind.REQUEST, session_id=session.id)

    created = await message_crud.create_message(db_session, msg)

    assert created is not None
    assert created.id is not None
    assert created.kind == MessageKind.REQUEST
    assert created.session_id == session.id


async def test_create_messages_batch(db_session: AsyncDbSession, session: Session) -> None:
    """Test creating multiple messages in batch."""
    messages = [
        Message(kind=MessageKind.REQUEST, session_id=session.id),
        Message(kind=MessageKind.RESPONSE, session_id=session.id),
        Message(kind=MessageKind.REQUEST, session_id=session.id),
    ]

    await message_crud.create_messages(db_session, messages)

    count = await message_crud.get_message_count(db_session, session.id)

    assert count == 3


def _seed_state_messages(session: Session, states: list[dict[str, object] | None]) -> list[Message]:
    """Build (unpersisted) response messages with the given states and ordered timestamps."""
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


async def test_find_previous_state_latest(db_session: AsyncDbSession, session: Session) -> None:
    """step -1 returns the state of the most recent message with state."""
    states: list[dict[str, object] | None] = [{"entities": {"a": {"f": "1"}}}, None]
    messages = _seed_state_messages(session, states)
    await message_crud.create_messages(db_session, messages)

    state = await message_crud.find_previous_state(db_session, session.id, -1)

    assert state == {"entities": {"a": {"f": "1"}}}


async def test_find_previous_state_at_step(db_session: AsyncDbSession, session: Session) -> None:
    """Returns the most recent state at or before the target step."""
    states: list[dict[str, object] | None] = [
        {"entities": {"a": {"f": "1"}}},
        None,
        {"entities": {"a": {"f": "2"}}},
        None,
        {"entities": {"a": {"f": "3"}}},
    ]
    await message_crud.create_messages(db_session, _seed_state_messages(session, states))

    assert await message_crud.find_previous_state(db_session, session.id, 0) == {
        "entities": {"a": {"f": "1"}}
    }
    assert await message_crud.find_previous_state(db_session, session.id, 1) == {
        "entities": {"a": {"f": "1"}}
    }
    assert await message_crud.find_previous_state(db_session, session.id, 2) == {
        "entities": {"a": {"f": "2"}}
    }
    assert await message_crud.find_previous_state(db_session, session.id, 4) == {
        "entities": {"a": {"f": "3"}}
    }


async def test_find_previous_state_walks_past_gaps(
    db_session: AsyncDbSession, session: Session
) -> None:
    """Messages with null state (gaps) are skipped while walking back."""
    states: list[dict[str, object] | None] = [
        {"entities": {"a": {"f": "first"}}},
        None,
        None,
        None,
    ]
    await message_crud.create_messages(db_session, _seed_state_messages(session, states))

    for step in range(4):
        state = await message_crud.find_previous_state(db_session, session.id, step)
        assert state == {"entities": {"a": {"f": "first"}}}


async def test_find_previous_state_no_state_exists(
    db_session: AsyncDbSession, session: Session
) -> None:
    """Returns None when no message has state (empty or all-gap history)."""
    assert await message_crud.find_previous_state(db_session, session.id, -1) is None

    gap_states: list[dict[str, object] | None] = [None, None]
    await message_crud.create_messages(db_session, _seed_state_messages(session, gap_states))

    assert await message_crud.find_previous_state(db_session, session.id, 0) is None
    assert await message_crud.find_previous_state(db_session, session.id, 1) is None


async def test_find_previous_state_invalid_step(
    db_session: AsyncDbSession, session: Session
) -> None:
    with pytest.raises(ValueError, match="Invalid step number"):
        await message_crud.find_previous_state(db_session, session.id, -2)


async def test_get_state_snapshots_ascending_with_gaps(
    db_session: AsyncDbSession, session: Session
) -> None:
    """Snapshots are listed in ascending step order, skipping gap messages."""
    base = datetime(2024, 1, 1, 12, 0, 0, tzinfo=UTC)
    naive_base = base.replace(tzinfo=None)  # SQLite round-trip drops tzinfo
    states: list[dict[str, object] | None] = [
        None,
        None,
        {"entities": {"a": {"f": "1"}}},
        None,
        None,
        {"entities": {"a": {"f": "2"}, "b": {"g": "3"}}},
        None,
        {"entities": {"c": {"h": "4"}}},
    ]
    await message_crud.create_messages(db_session, _seed_state_messages(session, states))

    snapshots = await message_crud.get_state_snapshots(db_session, session.id)

    assert [s.step for s in snapshots] == [2, 5, 7]
    assert [s.field_count for s in snapshots] == [1, 2, 1]
    assert [s.created_at for s in snapshots] == [
        naive_base + timedelta(minutes=2),
        naive_base + timedelta(minutes=5),
        naive_base + timedelta(minutes=7),
    ]


async def test_get_state_snapshots_empty_when_stateless(
    db_session: AsyncDbSession, session: Session
) -> None:
    """No snapshots for a session without messages or without any state."""
    assert await message_crud.get_state_snapshots(db_session, session.id) == []

    gap_states: list[dict[str, object] | None] = [None, None]
    await message_crud.create_messages(db_session, _seed_state_messages(session, gap_states))

    assert await message_crud.get_state_snapshots(db_session, session.id) == []


async def test_cleanup_state_history_noop_under_limit(
    db_session: AsyncDbSession, session: Session
) -> None:
    states: list[dict[str, object] | None] = [{"entities": {"a": {"f": str(i)}}} for i in range(3)]
    await message_crud.create_messages(db_session, _seed_state_messages(session, states))

    removed = await message_crud.cleanup_state_history(db_session, session.id, 5)

    assert removed == 0
    messages = await message_crud.get_messages(db_session, session.id)
    assert all(m.state is not None for m in messages)


async def test_cleanup_state_history_removes_oldest(
    db_session: AsyncDbSession, session: Session
) -> None:
    states: list[dict[str, object] | None] = [{"entities": {"a": {"f": str(i)}}} for i in range(5)]
    await message_crud.create_messages(db_session, _seed_state_messages(session, states))

    removed = await message_crud.cleanup_state_history(db_session, session.id, 2)

    assert removed == 3
    messages = await message_crud.get_messages(db_session, session.id)
    assert [m.state for m in messages] == [None, None, None, states[3], states[4]]


async def test_cleanup_state_history_ignores_gap_messages(
    db_session: AsyncDbSession, session: Session
) -> None:
    """Only messages with state count against the limit."""
    states: list[dict[str, object] | None] = [
        {"entities": {"a": {"f": "1"}}},
        None,
        {"entities": {"a": {"f": "2"}}},
        None,
        {"entities": {"a": {"f": "3"}}},
    ]
    await message_crud.create_messages(db_session, _seed_state_messages(session, states))

    removed = await message_crud.cleanup_state_history(db_session, session.id, 2)

    assert removed == 1
    messages = await message_crud.get_messages(db_session, session.id)
    assert messages[0].state is None
    assert messages[1].state is None
    assert messages[2].state == {"entities": {"a": {"f": "2"}}}
    assert messages[3].state is None
    assert messages[4].state == {"entities": {"a": {"f": "3"}}}


async def test_cleanup_state_history_invalid_limit(
    db_session: AsyncDbSession, session: Session
) -> None:
    with pytest.raises(ValueError, match="max_snapshots must be at least 1"):
        await message_crud.cleanup_state_history(db_session, session.id, 0)
