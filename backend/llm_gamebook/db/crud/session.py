from collections.abc import Sequence
from uuid import UUID

from sqlalchemy.orm import with_expression
from sqlmodel import col, desc, func, select
from sqlmodel.ext.asyncio.session import AsyncSession as AsyncDbSession

from llm_gamebook.db.models import Message, ModelConfig, Session


async def create_session(
    db_session: AsyncDbSession, model_config: ModelConfig, project_id: str, title: str | None = None
) -> Session:
    session = Session(title=title, project_id=project_id, config=model_config)
    db_session.add(session)
    await db_session.commit()
    await db_session.refresh(session)
    return session


async def get_sessions(
    db_session: AsyncDbSession, project_id: str | None, skip: int, limit: int
) -> Sequence[Session]:
    stmt = (
        select(Session)
        .outerjoin(Message, col(Message.session_id) == Session.id)
        .group_by(col(Session.id))
        .order_by(desc(Session.timestamp).nulls_last())
        .offset(skip)
        .limit(limit)
    )

    if project_id:
        stmt = stmt.where(Session.project_id == project_id)

    stmt = stmt.options(
        with_expression(
            Session.message_count,
            func.count(col(Message.id)),
        )
    )

    result = await db_session.exec(stmt)
    return result.all()


async def get_session_count(db_session: AsyncDbSession, project_id: str | None) -> int:
    stmt = select(func.count()).select_from(Session)

    if project_id:
        stmt = stmt.where(Session.project_id == project_id)

    result = await db_session.exec(stmt)
    return result.one()


async def get_session(db_session: AsyncDbSession, session_id: UUID) -> Session | None:
    stmt = (
        select(Session)
        .where(Session.id == session_id)
        .outerjoin(Message, col(Message.session_id) == Session.id)
        .group_by(col(Session.id))
        .options(
            with_expression(
                Session.message_count,
                func.count(col(Message.id)),
            )
        )
    )

    result = await db_session.exec(stmt)
    return result.one_or_none()


async def update_session_model_config(
    db_session: AsyncDbSession, session_id: UUID, config_id: UUID | None
) -> None:
    session = await db_session.get(Session, session_id)
    if session:
        session.config_id = config_id
        await db_session.commit()


async def delete_session(db_session: AsyncDbSession, session_id: UUID) -> None:
    session = await db_session.get(Session, session_id)
    await db_session.delete(session)
    await db_session.commit()
