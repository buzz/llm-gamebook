from datetime import datetime

from sqlmodel.ext.asyncio.session import AsyncSession as AsyncDbSession

from llm_gamebook.db.models import ModelConfig, Session
from llm_gamebook.db.models.message import Message, MessageKind


async def test_session_creation(db_session: AsyncDbSession, model_config: ModelConfig) -> None:
    session_obj = Session(title="New Test Session", config=model_config)
    db_session.add(session_obj)
    await db_session.commit()

    assert session_obj.id is not None
    assert session_obj.title == "New Test Session"
    assert session_obj.config_id == model_config.id
    assert session_obj.timestamp is not None


async def test_session_fields(db_session: AsyncDbSession, session: Session) -> None:
    assert session.id is not None
    assert session.title == "Test Session"
    assert session.timestamp is not None
    assert isinstance(session.timestamp, datetime)


async def test_session_relationships(
    db_session: AsyncDbSession, session: Session, model_config: ModelConfig
) -> None:
    assert session.config is not None
    assert session.config.id == model_config.id
    assert session.config.name == model_config.name

    message = Message(
        kind=MessageKind.REQUEST,
        session=session,
        model_name="test-model",
        finish_reason=None,
        timestamp=None,
    )
    db_session.add(message)
    await db_session.commit()
    await db_session.refresh(message)

    assert message.session_id == session.id
    assert message.session is not None
