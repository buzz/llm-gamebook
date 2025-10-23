from collections.abc import Sequence
from uuid import UUID

from sqlmodel import func, select
from sqlmodel.ext.asyncio.session import AsyncSession as AsyncDbSession

from llm_gamebook.db.models import Session


async def create_session(db_session: AsyncDbSession, session: Session) -> Session:
    db_session.add(session)
    await db_session.commit()
    await db_session.refresh(session)
    return session


async def get_sessions(db_session: AsyncDbSession, skip: int, limit: int) -> Sequence[Session]:
    statement = select(Session).offset(skip).limit(limit)
    result = await db_session.exec(statement)
    return result.all()


async def get_session_count(db_session: AsyncDbSession) -> int:
    statement = select(func.count()).select_from(Session)
    result = await db_session.exec(statement)
    return result.one()


async def get_session(db_session: AsyncDbSession, session_id: UUID) -> Session | None:
    return await db_session.get(Session, session_id)


async def delete_session(db_session: AsyncDbSession, session_id: UUID) -> None:
    session = await db_session.get(Session, session_id)
    await db_session.delete(session)
    await db_session.commit()
