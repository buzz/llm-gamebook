import pytest

from llm_gamebook.db.models import Session


@pytest.mark.skip
async def test_engine_manager_get_existing(session: Session, db_session, bus) -> None:
    pass


@pytest.mark.skip
async def test_engine_manager_get_or_create_new(session: Session, db_session, bus) -> None:
    pass


@pytest.mark.skip
async def test_engine_manager_get_or_create_existing(session: Session, db_session, bus) -> None:
    pass


@pytest.mark.skip
async def test_engine_manager_create_model_and_state(session: Session, db_session, bus) -> None:
    pass


@pytest.mark.skip
async def test_engine_manager_create_model_and_state_missing_session(
    session: Session, db_session, bus
) -> None:
    pass


@pytest.mark.skip
async def test_engine_manager_create_model_and_state_missing_config(
    session: Session, db_session, bus
) -> None:
    pass


@pytest.mark.skip
async def test_engine_manager_evict_idle(session: Session, db_session, bus) -> None:
    pass


@pytest.mark.skip
def test_engine_manager_drop_engine(session: Session, bus) -> None:
    pass


@pytest.mark.skip
def test_engine_manager_drop_engine_invalid_type(bus) -> None:
    pass


@pytest.mark.skip
async def test_engine_manager_context_manager(bus) -> None:
    pass
