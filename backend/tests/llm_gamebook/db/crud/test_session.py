from uuid import uuid4

from sqlmodel.ext.asyncio.session import AsyncSession as AsyncDbSession

from llm_gamebook.db.crud import session as session_crud
from llm_gamebook.db.models import ModelConfig, Session


async def test_create_session(db_session: AsyncDbSession, model_config: ModelConfig) -> None:
    created_session = await session_crud.create_session(
        db_session, model_config, title="New Test Session"
    )

    assert created_session is not None
    assert created_session.id is not None
    assert created_session.title == "New Test Session"
    assert created_session.config_id == model_config.id


async def test_get_sessions_empty(db_session: AsyncDbSession) -> None:
    sessions = await session_crud.get_sessions(db_session, skip=0, limit=10)

    assert sessions == []


async def test_get_sessions_with_data(
    db_session: AsyncDbSession, model_config: ModelConfig
) -> None:
    await session_crud.create_session(db_session, model_config, title="Session 1")
    await session_crud.create_session(db_session, model_config, title="Session 2")

    sessions = await session_crud.get_sessions(db_session, skip=0, limit=10)

    assert len(sessions) == 2
    assert sessions[0].title == "Session 1"
    assert sessions[1].title == "Session 2"


async def test_get_session_count(db_session: AsyncDbSession, model_config: ModelConfig) -> None:
    initial_count = await session_crud.get_session_count(db_session)

    await session_crud.create_session(db_session, model_config, title="Test Session")

    new_count = await session_crud.get_session_count(db_session)

    assert new_count == initial_count + 1


async def test_get_session_found(db_session: AsyncDbSession, session: Session) -> None:
    found_session = await session_crud.get_session(db_session, session.id)

    assert found_session is not None
    assert found_session.id == session.id


async def test_get_session_not_found(db_session: AsyncDbSession) -> None:
    non_existent_id = uuid4()

    found_session = await session_crud.get_session(db_session, non_existent_id)

    assert found_session is None


async def test_update_session_model_config(
    db_session: AsyncDbSession, session: Session, model_config: ModelConfig
) -> None:
    await session_crud.update_session_model_config(db_session, session.id, model_config.id)
    await db_session.refresh(session)

    assert session.config_id == model_config.id


async def test_delete_session(db_session: AsyncDbSession, session: Session) -> None:
    session_id = session.id

    await session_crud.delete_session(db_session, session_id)

    deleted_session = await session_crud.get_session(db_session, session_id)

    assert deleted_session is None
