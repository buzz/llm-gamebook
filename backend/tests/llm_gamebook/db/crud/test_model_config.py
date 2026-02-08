from uuid import uuid4

from sqlmodel.ext.asyncio.session import AsyncSession as AsyncDbSession

from llm_gamebook.db.crud.model_config import (
    create_model_config,
    delete_model_config,
    get_model_config,
    get_model_config_count,
    get_model_configs,
    update_model_config,
)
from llm_gamebook.db.models import ModelConfig
from llm_gamebook.providers import ModelProvider
from llm_gamebook.web.schema.model_config import ModelConfigUpdate


async def test_create_model_config(db_session: AsyncDbSession) -> None:
    config = ModelConfig(
        name="Test Model",
        provider=ModelProvider.OPENAI,
        model_name="gpt-4o",
        base_url="https://api.openai.com/v1",
        api_key="test-key",
        context_window=4096,
        max_tokens=1024,
        temperature=0.7,
        top_p=0.9,
        presence_penalty=0.0,
        frequency_penalty=0.0,
    )
    result = await create_model_config(db_session, config)
    assert result.id is not None
    assert result.name == "Test Model"
    assert result.provider == ModelProvider.OPENAI
    assert result.model_name == "gpt-4o"


async def test_get_model_configs_empty(db_session: AsyncDbSession) -> None:
    configs = await get_model_configs(db_session)
    assert configs == []


async def test_get_model_configs_with_data(db_session: AsyncDbSession) -> None:
    config1 = ModelConfig(
        name="Config 1",
        provider=ModelProvider.OPENAI,
        model_name="gpt-4",
        context_window=4096,
        max_tokens=1024,
        temperature=0.7,
        top_p=0.9,
        presence_penalty=0.0,
        frequency_penalty=0.0,
    )
    config2 = ModelConfig(
        name="Config 2",
        provider=ModelProvider.ANTHROPIC,
        model_name="claude-3-5-sonnet",
        context_window=4096,
        max_tokens=1024,
        temperature=0.7,
        top_p=0.9,
        presence_penalty=0.0,
        frequency_penalty=0.0,
    )
    await create_model_config(db_session, config1)
    await create_model_config(db_session, config2)
    configs = await get_model_configs(db_session)
    assert len(configs) == 2
    assert configs[0].name == "Config 1"
    assert configs[1].name == "Config 2"


async def test_get_model_config_count(db_session: AsyncDbSession) -> None:
    count = await get_model_config_count(db_session)
    assert count == 0
    config = ModelConfig(
        name="Test",
        provider=ModelProvider.OPENAI,
        model_name="gpt-4",
        context_window=4096,
        max_tokens=1024,
        temperature=0.7,
        top_p=0.9,
        presence_penalty=0.0,
        frequency_penalty=0.0,
    )
    await create_model_config(db_session, config)
    count = await get_model_config_count(db_session)
    assert count == 1


async def test_get_model_config_found(
    db_session: AsyncDbSession, model_config: ModelConfig
) -> None:
    config = await get_model_config(db_session, model_config.id)
    assert config is not None
    assert config.id == model_config.id
    assert config.name == "Test Config"


async def test_get_model_config_not_found(db_session: AsyncDbSession) -> None:
    fake_id = uuid4()
    config = await get_model_config(db_session, fake_id)
    assert config is None


async def test_update_model_config(db_session: AsyncDbSession, model_config: ModelConfig) -> None:
    update = ModelConfigUpdate(
        name="Updated Name",
        provider=ModelProvider.OPENAI,
        model_name="gpt-4o",
        context_window=4096,
        max_tokens=2048,
        temperature=0.5,
        top_p=0.8,
        presence_penalty=0.1,
        frequency_penalty=0.1,
    )
    await update_model_config(db_session, str(model_config.id), update)
    config = await get_model_config(db_session, model_config.id)
    assert config is not None
    assert config.name == "Updated Name"
    assert config.model_name == "gpt-4o"
    assert config.max_tokens == 2048


async def test_delete_model_config(db_session: AsyncDbSession, model_config: ModelConfig) -> None:
    await delete_model_config(db_session, str(model_config.id))
    config = await get_model_config(db_session, model_config.id)
    assert config is None
