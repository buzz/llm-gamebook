import pytest
from sqlalchemy.exc import IntegrityError
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession as AsyncDbSession

from llm_gamebook.db.models import UserSettings
from llm_gamebook.db.models.user_settings import ChatView


async def test_user_settings_creation(db_session: AsyncDbSession) -> None:
    """Test creating a UserSettings record with all fields."""
    settings = UserSettings(chat_view=ChatView.DETAILS, enter_submits_message=True)
    db_session.add(settings)
    await db_session.commit()
    await db_session.refresh(settings)

    assert settings.id == "settings"
    assert settings.chat_view == ChatView.DETAILS
    assert settings.enter_submits_message is True


async def test_user_settings_default_values(db_session: AsyncDbSession) -> None:
    """Test that default values are applied correctly."""
    settings = UserSettings()
    db_session.add(settings)
    await db_session.commit()
    await db_session.refresh(settings)

    assert settings.id == "settings"
    assert settings.chat_view == ChatView.STANDARD
    assert settings.enter_submits_message is True


async def test_user_settings_update(db_session: AsyncDbSession) -> None:
    """Test updating UserSettings fields."""
    settings = UserSettings()
    db_session.add(settings)
    await db_session.commit()
    await db_session.refresh(settings)

    # Update fields
    settings.chat_view = ChatView.DETAILS
    settings.enter_submits_message = False

    await db_session.commit()
    await db_session.refresh(settings)

    assert settings.id == "settings"
    assert settings.chat_view == ChatView.DETAILS
    assert settings.enter_submits_message is False


async def test_user_settings_single_record_per_user(db_session: AsyncDbSession) -> None:
    """Test that only one settings record exists per user (single user constraint)."""
    # Create first settings record
    settings1 = UserSettings(chat_view=ChatView.STANDARD, enter_submits_message=True)
    db_session.add(settings1)
    await db_session.commit()
    await db_session.refresh(settings1)

    settings1_id = settings1.id

    # Verify querying returns exactly one record
    result = await db_session.exec(select(UserSettings))
    all_settings = result.all()

    assert len(all_settings) == 1
    assert all_settings[0].id == settings1_id

    # Try to create a second settings record - should fail due to primary key constraint
    settings2 = UserSettings(chat_view=ChatView.STANDARD, enter_submits_message=False)
    db_session.add(settings2)

    with pytest.raises(IntegrityError):
        await db_session.commit()

    await db_session.rollback()


async def test_user_settings_persistence(db_session: AsyncDbSession) -> None:
    """Test that UserSettings persists correctly and can be retrieved."""
    settings = UserSettings(chat_view=ChatView.DETAILS, enter_submits_message=False)
    db_session.add(settings)
    await db_session.commit()
    await db_session.refresh(settings)

    settings_id = settings.id

    # Query the settings again
    result = await db_session.exec(select(UserSettings).where(UserSettings.id == settings_id))
    retrieved = result.first()

    assert retrieved is not None
    assert retrieved.id == settings_id
    assert retrieved.chat_view == ChatView.DETAILS
    assert retrieved.enter_submits_message is False


@pytest.mark.parametrize("chat_view", [ChatView.STANDARD, ChatView.DETAILS, ChatView.DEBUG])
async def test_user_settings_different_chat_views(
    db_session: AsyncDbSession, chat_view: ChatView
) -> None:
    """Test different valid chat_view values."""
    settings = UserSettings(chat_view=chat_view, enter_submits_message=True)
    db_session.add(settings)
    await db_session.commit()
    await db_session.refresh(settings)

    assert settings.chat_view == chat_view
    assert settings.enter_submits_message is True


@pytest.mark.parametrize("value", [True, False])
async def test_user_settings_enter_submits_message_boolean(
    db_session: AsyncDbSession, *, value: bool
) -> None:
    """Test enter_submits_message accepts boolean values."""
    settings = UserSettings(chat_view=ChatView.STANDARD, enter_submits_message=value)
    db_session.add(settings)
    await db_session.commit()
    await db_session.refresh(settings)

    assert settings.enter_submits_message is value
