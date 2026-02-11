from uuid import uuid4

import pytest
from sqlmodel.ext.asyncio.session import AsyncSession as AsyncDbSession

from llm_gamebook.db.models import Session
from llm_gamebook.engine.manager import EngineManager
from llm_gamebook.message_bus import MessageBus


async def test_engine_manager_get_or_create_new(
    session: Session, db_session: AsyncDbSession, message_bus: MessageBus
) -> None:
    engine_mgr = EngineManager(message_bus)

    engine = await engine_mgr.get_or_create(session.id, db_session)

    assert engine is not None
    assert engine.session_adapter.session_id == session.id


async def test_engine_manager_get_or_create_returns_same_engine(
    session: Session, db_session: AsyncDbSession, message_bus: MessageBus
) -> None:
    engine_mgr = EngineManager(message_bus)

    engine1 = await engine_mgr.get_or_create(session.id, db_session)
    engine2 = await engine_mgr.get_or_create(session.id, db_session)

    assert engine1 is engine2


async def test_engine_manager_get_or_create_does_not_reinstantiate_for_existing(
    session: Session, db_session: AsyncDbSession, message_bus: MessageBus
) -> None:
    engine_mgr = EngineManager(message_bus)

    engine1 = await engine_mgr.get_or_create(session.id, db_session)
    engine2 = await engine_mgr.get_or_create(session.id, db_session)

    assert engine1 is engine2


async def test_engine_manager_create_model_and_state(
    session: Session, db_session: AsyncDbSession, message_bus: MessageBus
) -> None:
    engine_mgr = EngineManager(message_bus)

    model, state = await engine_mgr._create_model_and_state(session.id, db_session)

    assert model is not None
    assert state is not None


async def test_engine_manager_create_model_and_state_missing_session(
    db_session: AsyncDbSession, message_bus: MessageBus
) -> None:
    engine_mgr = EngineManager(message_bus)
    non_existent_session_id = uuid4()

    with pytest.raises(ValueError, match=r"Session .* or its config not found"):
        await engine_mgr._create_model_and_state(non_existent_session_id, db_session)


async def test_engine_manager_evict_idle(
    session: Session, db_session: AsyncDbSession, message_bus: MessageBus
) -> None:
    engine_mgr = EngineManager(message_bus, max_idle_seconds=1)

    engine = await engine_mgr.get_or_create(session.id, db_session)
    assert engine is not None

    await engine_mgr._evict_idle()
    assert session.id not in engine_mgr._engines


def test_engine_manager_drop_engine(session: Session, message_bus: MessageBus) -> None:
    engine_mgr = EngineManager(message_bus)

    engine_mgr._drop_engine(session.id)

    assert session.id not in engine_mgr._engines


async def test_engine_manager_context_manager(message_bus: MessageBus) -> None:
    async with EngineManager(message_bus) as engine_mgr:
        assert engine_mgr._evict_task is not None

    assert engine_mgr._evict_task.done()


async def test_engine_manager_lazy_initialization_on_first_request(
    session: Session, db_session: AsyncDbSession, message_bus: MessageBus
) -> None:
    engine_mgr = EngineManager(message_bus)

    engine = await engine_mgr.get_or_create(session.id, db_session)

    assert engine is not None
    assert session.id in engine_mgr._engines


async def test_engine_manager_does_not_create_engine_until_requested(
    session: Session, db_session: AsyncDbSession, message_bus: MessageBus
) -> None:
    engine_mgr = EngineManager(message_bus)

    assert session.id not in engine_mgr._engines

    engine = await engine_mgr.get_or_create(session.id, db_session)

    assert session.id in engine_mgr._engines
    assert engine is not None
