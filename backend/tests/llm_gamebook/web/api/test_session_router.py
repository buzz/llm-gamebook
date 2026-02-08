import pytest
from sqlmodel.ext.asyncio.session import AsyncSession as AsyncDbSession

from llm_gamebook.db.models.session import Session
from llm_gamebook.engine.engine import StoryEngine


@pytest.mark.skip
async def test_read_sessions_empty(db_session: AsyncDbSession) -> None:
    pass


@pytest.mark.skip
async def test_read_sessions_with_pagination(db_session: AsyncDbSession) -> None:
    pass


@pytest.mark.skip
async def test_read_session_found(engine: StoryEngine, db_session: AsyncDbSession) -> None:
    pass


@pytest.mark.skip
async def test_read_session_not_found(engine: StoryEngine, db_session: AsyncDbSession) -> None:
    pass


@pytest.mark.skip
async def test_create_session_success(db_session: AsyncDbSession) -> None:
    pass


@pytest.mark.skip
async def test_create_session_model_config_not_found(db_session: AsyncDbSession) -> None:
    pass


@pytest.mark.skip
async def test_update_session(
    engine: StoryEngine, db_session: AsyncDbSession, session: Session
) -> None:
    pass


@pytest.mark.skip
async def test_create_model_request(engine: StoryEngine, db_session: AsyncDbSession) -> None:
    pass


@pytest.mark.skip
async def test_delete_session(engine: StoryEngine, db_session: AsyncDbSession) -> None:
    pass
