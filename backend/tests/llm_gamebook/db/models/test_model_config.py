from sqlmodel.ext.asyncio.session import AsyncSession as AsyncDbSession

from llm_gamebook.db.models import ModelConfig
from llm_gamebook.providers import ModelProvider


async def test_model_config_creation(db_session: AsyncDbSession) -> None:
    config = ModelConfig(
        name="Test Config",
        provider=ModelProvider.OPENAI_COMPATIBLE,
        model_name="gpt-4",
        base_url="http://localhost:5001/v1",
        api_key="test-key-12345",
        context_window=4096,
        max_tokens=1024,
        temperature=0.7,
        top_p=0.9,
        presence_penalty=0.0,
        frequency_penalty=0.0,
    )
    db_session.add(config)
    await db_session.commit()
    await db_session.refresh(config)

    assert config.id is not None
    assert config.name == "Test Config"
    assert config.provider == ModelProvider.OPENAI_COMPATIBLE
    assert config.model_name == "gpt-4"
    assert config.base_url == "http://localhost:5001/v1"
    assert config.api_key == "test-key-12345"
    assert config.context_window == 4096
    assert config.max_tokens == 1024
    assert config.temperature == 0.7
    assert config.top_p == 0.9
    assert config.presence_penalty == 0.0
    assert config.frequency_penalty == 0.0


async def test_model_config_fields(db_session: AsyncDbSession, model_config: ModelConfig) -> None:
    await db_session.refresh(model_config)

    assert model_config.id is not None
    assert model_config.name == "Test Config"
    assert model_config.provider == ModelProvider.OPENAI_COMPATIBLE
    assert model_config.model_name == "gpt-4"
    assert model_config.base_url == "http://localhost:5001/v1"
    assert model_config.api_key == "test-key-12345"
    assert model_config.context_window == 4096
    assert model_config.max_tokens == 1024
    assert model_config.temperature == 0.7
    assert model_config.top_p == 0.9
    assert model_config.presence_penalty == 0.0
    assert model_config.frequency_penalty == 0.0


async def test_model_config_with_null_fields(db_session: AsyncDbSession) -> None:
    config = ModelConfig(
        name="Minimal Config",
        provider=ModelProvider.ANTHROPIC,
        model_name="claude-3-5-sonnet",
        base_url=None,
        api_key=None,
        context_window=200000,
        max_tokens=4096,
        temperature=1.0,
        top_p=0.99,
        presence_penalty=0.0,
        frequency_penalty=0.0,
    )
    db_session.add(config)
    await db_session.commit()
    await db_session.refresh(config)

    assert config.id is not None
    assert config.name == "Minimal Config"
    assert config.base_url is None
    assert config.api_key is None


async def test_model_config_update(db_session: AsyncDbSession, model_config: ModelConfig) -> None:
    await db_session.refresh(model_config)

    original_id = model_config.id

    model_config.name = "Updated Config Name"
    model_config.temperature = 0.5
    model_config.max_tokens = 2048

    await db_session.commit()
    await db_session.refresh(model_config)

    assert model_config.id == original_id
    assert model_config.name == "Updated Config Name"
    assert model_config.temperature == 0.5
    assert model_config.max_tokens == 2048
