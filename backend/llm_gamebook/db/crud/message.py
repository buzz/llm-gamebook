from collections.abc import Iterable, Sequence
from uuid import UUID

from sqlmodel import desc, func, select
from sqlmodel.ext.asyncio.session import AsyncSession as AsyncDbSession
from sqlmodel.sql.expression import SelectOfScalar

from llm_gamebook.db.models import Message


def _get_select_by_session_id(session_id: UUID) -> SelectOfScalar[Message]:
    return (
        select(Message)
        .where(Message.session_id == session_id)
        .order_by(desc(Message.timestamp).nulls_last())
    )


async def get_message_count(db_session: AsyncDbSession, session_id: UUID) -> int:
    statement = select(func.count()).select_from(Message).where(Message.session_id == session_id)
    return (await db_session.exec(statement)).one()


async def get_messages(db_session: AsyncDbSession, session_id: UUID) -> Sequence[Message]:
    result = await db_session.exec(_get_select_by_session_id(session_id))
    return result.all()


async def create_message(db_session: AsyncDbSession, message: Message) -> Message:
    db_session.add(message)
    await db_session.commit()
    await db_session.refresh(message)
    return message


async def create_messages(db_session: AsyncDbSession, messages: Iterable[Message]) -> None:
    db_session.add_all(messages)
    await db_session.commit()
