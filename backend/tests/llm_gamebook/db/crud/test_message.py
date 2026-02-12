
import pytest
from sqlmodel.ext.asyncio.session import AsyncSession as AsyncDbSession

from llm_gamebook.db.models import Session


@pytest.mark.skip(reason="Not yet implemented")
async def test_get_message_count(db_session: AsyncDbSession, session: Session) -> None:
    """Test counting messages for a session."""


@pytest.mark.skip(reason="Not yet implemented")
async def test_get_message_count_empty(db_session: AsyncDbSession, session: Session) -> None:
    """Test counting messages when session has no messages."""


@pytest.mark.skip(reason="Not yet implemented")
async def test_get_messages(db_session: AsyncDbSession, session: Session) -> None:
    """Test retrieving messages for a session with ordering."""


@pytest.mark.skip(reason="Not yet implemented")
async def test_get_messages_empty(db_session: AsyncDbSession, session: Session) -> None:
    """Test retrieving messages when session has no messages."""


@pytest.mark.skip(reason="Not yet implemented")
async def test_create_message(db_session: AsyncDbSession, session: Session) -> None:
    """Test creating a single message."""


@pytest.mark.skip(reason="Not yet implemented")
async def test_create_messages_batch(db_session: AsyncDbSession, session: Session) -> None:
    """Test creating multiple messages in batch."""
