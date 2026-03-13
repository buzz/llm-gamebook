from collections.abc import Iterable, Sequence
from uuid import UUID

from sqlmodel import asc, desc, func, select
from sqlmodel.ext.asyncio.session import AsyncSession as AsyncDbSession

from llm_gamebook.db.models import Message


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
