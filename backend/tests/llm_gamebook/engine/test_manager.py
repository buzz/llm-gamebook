from uuid import uuid4

import pytest
from sqlmodel.ext.asyncio.session import AsyncSession as AsyncDbSession

from llm_gamebook.db.models import Session
from llm_gamebook.engine.manager import EngineManager
from llm_gamebook.message_bus import MessageBus


async def test_engine_manager_get_or_create_new(
    session: Session, db_session: AsyncDbSession, engine_manager: EngineManager
) -> None:
    engine = await engine_manager.get_or_create(session.id, db_session)

    assert engine.session_adapter.session_id == session.id


async def test_engine_manager_get_or_create_returns_same_engine(
    session: Session, db_session: AsyncDbSession, engine_manager: EngineManager
) -> None:
    engine1 = await engine_manager.get_or_create(session.id, db_session)
    engine2 = await engine_manager.get_or_create(session.id, db_session)

    assert engine1 is engine2


async def test_engine_manager_get_or_create_does_not_reinstantiate_for_existing(
    session: Session, db_session: AsyncDbSession, engine_manager: EngineManager
) -> None:
    engine1 = await engine_manager.get_or_create(session.id, db_session)
    engine2 = await engine_manager.get_or_create(session.id, db_session)

    assert engine1 is engine2


async def test_engine_manager_create_model_and_state(
    session: Session, db_session: AsyncDbSession, engine_manager: EngineManager
) -> None:
    model, state = await engine_manager._create_model_and_state(session.id, db_session)

    assert model is not None
    assert state is not None


async def test_engine_manager_create_model_and_state_missing_session(
    db_session: AsyncDbSession, engine_manager: EngineManager
) -> None:
    non_existent_session_id = uuid4()

    with pytest.raises(ValueError, match=r"Session .* not found"):
        await engine_manager._create_model_and_state(non_existent_session_id, db_session)


async def test_engine_manager_evict_idle(
    session: Session, db_session: AsyncDbSession, message_bus: MessageBus
) -> None:
    async with EngineManager(message_bus, max_idle_seconds=1) as engine_manager:
        engine = await engine_manager.get_or_create(session.id, db_session)
        assert engine is not None

        engine_manager._engines[session.id] = (engine, 0)
        engine_manager._perform_eviction()
        assert session.id not in engine_manager._engines


async def test_engine_manager_drop_engine(
    session: Session, db_session: AsyncDbSession, engine_manager: EngineManager
) -> None:
    await engine_manager.get_or_create(session.id, db_session)
    engine_manager._drop_engine(session.id)

    assert session.id not in engine_manager._engines


async def test_engine_manager_context_manager(message_bus: MessageBus) -> None:
    async with EngineManager(message_bus) as engine_manager:
        assert engine_manager._evict_task is not None

    assert engine_manager._evict_task.done()


async def test_engine_manager_lazy_initialization_on_first_request(
    session: Session, db_session: AsyncDbSession, engine_manager: EngineManager
) -> None:
    engine = await engine_manager.get_or_create(session.id, db_session)

    assert engine is not None
    assert session.id in engine_manager._engines


async def test_engine_manager_does_not_create_engine_until_requested(
    session: Session, db_session: AsyncDbSession, engine_manager: EngineManager
) -> None:
    assert session.id not in engine_manager._engines

    engine = await engine_manager.get_or_create(session.id, db_session)

    assert engine is not None
    assert session.id in engine_manager._engines
