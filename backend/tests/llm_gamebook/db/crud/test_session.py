from uuid import uuid4

from sqlmodel.ext.asyncio.session import AsyncSession as AsyncDbSession

from llm_gamebook.db.crud import session as session_crud
from llm_gamebook.db.models import ModelConfig, Session


async def test_create_session(db_session: AsyncDbSession, model_config: ModelConfig) -> None:
    created_session = await session_crud.create_session(
        db_session, model_config, "foo/bar", "New Test Session"
    )

    assert created_session is not None
    assert created_session.id is not None
    assert created_session.project_id == "foo/bar"
    assert created_session.title == "New Test Session"
    assert created_session.config_id == model_config.id


async def test_get_sessions_empty(db_session: AsyncDbSession) -> None:
    sessions = await session_crud.get_sessions(db_session, project_id=None, skip=0, limit=10)

    assert sessions == []


async def test_get_sessions_with_data(
    db_session: AsyncDbSession, model_config: ModelConfig
) -> None:
    await session_crud.create_session(db_session, model_config, "foo/bar", "Session 1")
    await session_crud.create_session(db_session, model_config, "baz/quz", "Session 2")

    sessions = await session_crud.get_sessions(db_session, project_id=None, skip=0, limit=10)

    assert len(sessions) == 2
    assert sessions[0].title == "Session 2"
    assert sessions[1].title == "Session 1"


async def test_get_sessions_with_project_filter(
    db_session: AsyncDbSession, model_config: ModelConfig
) -> None:
    await session_crud.create_session(db_session, model_config, "foo/bar", "Session 1")
    await session_crud.create_session(db_session, model_config, "baz/quz", "Session 2")

    sessions = await session_crud.get_sessions(db_session, project_id="foo/bar", skip=0, limit=10)

    assert len(sessions) == 1
    assert sessions[0].project_id == "foo/bar"


async def test_get_session_count(db_session: AsyncDbSession, model_config: ModelConfig) -> None:
    initial_count = await session_crud.get_session_count(db_session, project_id=None)

    await session_crud.create_session(db_session, model_config, "foo/bar", "Test Session")

    new_count = await session_crud.get_session_count(db_session, project_id=None)

    assert new_count == initial_count + 1


async def test_get_session_count_with_project_filter(
    db_session: AsyncDbSession, model_config: ModelConfig
) -> None:
    await session_crud.create_session(db_session, model_config, "foo/bar", "Session 1")
    await session_crud.create_session(db_session, model_config, "baz/quz", "Session 2")

    count = await session_crud.get_session_count(db_session, project_id="foo/bar")

    assert count == 1


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


async def test_update_session_state(db_session: AsyncDbSession, model_config: ModelConfig) -> None:
    session = await session_crud.create_session(db_session, model_config, "foo/bar")
    snapshot: dict[str, object] = {"entities": {"a": {"f": "1"}}}

    updated = await session_crud.update_session_state(db_session, session.id, snapshot)

    assert updated is not None
    assert updated.state == snapshot


async def test_update_session_state_clears_state(
    db_session: AsyncDbSession, model_config: ModelConfig
) -> None:
    session = await session_crud.create_session(db_session, model_config, "foo/bar")
    await session_crud.update_session_state(db_session, session.id, {"entities": {}})

    updated = await session_crud.update_session_state(db_session, session.id, None)

    assert updated is not None
    assert updated.state is None


async def test_mark_session_ended(db_session: AsyncDbSession, model_config: ModelConfig) -> None:
    session = await session_crud.create_session(db_session, model_config, "foo/bar")
    assert session.ended_at is None

    ended = await session_crud.mark_session_ended(db_session, session.id)

    assert ended is not None
    assert ended.ended_at is not None


async def test_reset_session_clears_state_and_end(
    db_session: AsyncDbSession, model_config: ModelConfig
) -> None:
    session = await session_crud.create_session(db_session, model_config, "foo/bar")
    await session_crud.update_session_state(db_session, session.id, {"entities": {"a": {"f": "1"}}})
    await session_crud.mark_session_ended(db_session, session.id)

    reset = await session_crud.reset_session(db_session, session.id)

    assert reset is not None
    assert reset.state is None
    assert reset.ended_at is None


async def test_reset_session_is_idempotent(
    db_session: AsyncDbSession, model_config: ModelConfig
) -> None:
    session = await session_crud.create_session(db_session, model_config, "foo/bar")

    first = await session_crud.reset_session(db_session, session.id)
    second = await session_crud.reset_session(db_session, session.id)

    assert first is not None
    assert second is not None
    assert second.state is None
    assert second.ended_at is None


async def test_create_fork_session_copies_state(
    db_session: AsyncDbSession, model_config: ModelConfig
) -> None:
    source = await session_crud.create_session(
        db_session,
        model_config,
        "foo/bar",
        "Source",
    )
    snapshot: dict[str, object] = {"entities": {"a": {"f": "1"}}}

    fork = await session_crud.create_fork_session(db_session, source, snapshot)

    assert fork.id != source.id
    assert fork.project_id == source.project_id
    assert fork.config_id == source.config_id
    assert fork.state == snapshot
    assert fork.ended_at is None
    assert fork.title is None
    assert fork.messages == []


async def test_create_fork_session_leaves_source_unaffected(
    db_session: AsyncDbSession, model_config: ModelConfig
) -> None:
    source = await session_crud.create_session(
        db_session,
        model_config,
        "foo/bar",
        "Source",
    )

    await session_crud.create_fork_session(db_session, source, {"entities": {"a": {"f": "1"}}})
    reloaded = await session_crud.get_session(db_session, source.id)

    assert reloaded is not None
    assert reloaded.state is None
    assert reloaded.ended_at is None
