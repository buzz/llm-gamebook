from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from sqlmodel import asc, col, desc, func, select
from sqlmodel.ext.asyncio.session import AsyncSession as AsyncDbSession

from llm_gamebook.db.models import Message


@dataclass(frozen=True)
class StateSnapshot:
    """A stored state snapshot of a session message.

    Attributes:
        step: 0-based index of the snapshot's message within the session's messages.
        created_at: The snapshot message's timestamp.
        field_count: The number of entity fields changed in this snapshot.
    """

    step: int
    created_at: datetime | None
    field_count: int


async def get_message_count(db_session: AsyncDbSession, session_id: UUID) -> int:
    stmt = select(func.count()).select_from(Message).where(Message.session_id == session_id)
    result = await db_session.exec(stmt)

    return result.one()


async def get_messages(db_session: AsyncDbSession, session_id: UUID) -> Sequence[Message]:
    stmt = (
        select(Message)
        .where(Message.session_id == session_id)
        .order_by(asc(Message.timestamp).nulls_last())
    )

    result = await db_session.exec(stmt)
    return result.all()


async def create_message(db_session: AsyncDbSession, message: Message) -> Message:
    db_session.add(message)
    await db_session.commit()
    await db_session.refresh(message)
    return message


async def create_messages(db_session: AsyncDbSession, messages: Iterable[Message]) -> None:
    db_session.add_all(messages)
    await db_session.commit()


async def get_latest_message_with_state(
    db_session: AsyncDbSession, session_id: UUID
) -> Message | None:
    stmt = (
        select(Message)
        .where(Message.session_id == session_id)
        .order_by(desc(Message.timestamp).nulls_last())
    )
    result = await db_session.exec(stmt)
    for msg in result.all():
        if msg.state is not None:
            return msg
    return None


async def find_previous_state(
    db_session: AsyncDbSession, session_id: UUID, step_num: int
) -> dict[str, object] | None:
    """Find the state snapshot at or before the given step.

    Walks the session's messages from oldest to newest and returns the state
    of the most recent message with a non-null state at or before step_num.
    Messages without state (gaps) are skipped. A step_num of -1 targets the
    latest state.

    Args:
        db_session: The async database session.
        session_id: The session to search.
        step_num: The target step (0-based message index) or -1 for the
            latest state.

    Returns:
        The raw state dict of the most recent message with state at or
        before the target step, or None if no such message exists.
    """
    if step_num < -1:
        msg = f"Invalid step number: {step_num} (expected -1 for latest or a 0-based index)"
        raise ValueError(msg)

    messages = await get_messages(db_session, session_id)
    limit = len(messages) if step_num == -1 else step_num + 1
    state: dict[str, object] | None = None
    for message in messages[:limit]:
        if message.state is not None:
            state = message.state
    return state


async def cleanup_state_history(
    db_session: AsyncDbSession, session_id: UUID, max_snapshots: int
) -> int:
    """Remove the oldest state snapshots beyond max_snapshots.

    Only the most recent max_snapshots messages keep their state; older
    messages have their state cleared (set to None).

    Args:
        db_session: The async database session.
        session_id: The session to clean up.
        max_snapshots: Maximum number of state snapshots to keep.

    Returns:
        The number of state snapshots removed.
    """
    if max_snapshots < 1:
        msg = f"max_snapshots must be at least 1, got {max_snapshots}"
        raise ValueError(msg)

    stmt = (
        select(Message)
        .where(Message.session_id == session_id)
        .where(col(Message.state).is_not(None))
        .order_by(asc(Message.timestamp).nulls_last())
    )
    result = await db_session.exec(stmt)
    messages = result.all()

    overflow = len(messages) - max_snapshots
    if overflow <= 0:
        return 0

    for message in messages[:overflow]:
        message.state = None
    await db_session.commit()
    return overflow


def count_state_fields(state: dict[str, object]) -> int:
    """Count the number of entity fields changed in a raw state dict.

    Args:
        state: A raw state dict shaped like {"entities": {entity: {field: value}}}.

    Returns:
        The total number of entity fields present in the state dict (0 for
        malformed or empty state).
    """
    entities = state.get("entities")
    if not isinstance(entities, dict):
        return 0

    return sum(len(fields) for fields in entities.values() if isinstance(fields, dict))


async def get_state_snapshots(
    db_session: AsyncDbSession, session_id: UUID
) -> Sequence[StateSnapshot]:
    """List a session's stored state snapshots in ascending step order.

    Every message carrying a state yields one snapshot entry keyed by its
    0-based index within the session's message list. Messages without state
    (gaps) are skipped.

    Args:
        db_session: The async database session.
        session_id: The session to query.

    Returns:
        A sequence of snapshots in ascending step order (empty if the
        session has no stored state).
    """
    messages = await get_messages(db_session, session_id)
    snapshots: list[StateSnapshot] = []
    for index, message in enumerate(messages):
        if message.state is None:
            continue
        snapshots.append(
            StateSnapshot(
                step=index,
                created_at=message.timestamp,
                field_count=count_state_fields(message.state),
            )
        )
    return snapshots
