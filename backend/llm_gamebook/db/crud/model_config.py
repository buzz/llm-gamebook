from collections.abc import Sequence
from uuid import UUID

from sqlmodel import func, select
from sqlmodel.ext.asyncio.session import AsyncSession as AsyncDbSession

from llm_gamebook.db.models import ModelConfig
from llm_gamebook.web.schemas.model_config import ModelConfigUpdate


async def create_model_config(db_session: AsyncDbSession, config: ModelConfig) -> ModelConfig:
    db_session.add(config)
    await db_session.commit()
    await db_session.refresh(config)
    return config


async def get_model_configs(
    db_session: AsyncDbSession, skip: int = 0, limit: int = 100
) -> Sequence[ModelConfig]:
    statement = select(ModelConfig).offset(skip).limit(limit)
    result = await db_session.exec(statement)
    return result.all()


async def get_model_config_count(db_session: AsyncDbSession) -> int:
    statement = select(func.count()).select_from(ModelConfig)
    result = await db_session.exec(statement)
    return result.one()


async def get_model_config(db_session: AsyncDbSession, config_id: UUID) -> ModelConfig | None:
    return await db_session.get(ModelConfig, config_id)


async def update_model_config(
    db_session: AsyncDbSession,
    config_id: str,
    model_config_update: ModelConfigUpdate,
) -> None:
    config = await db_session.get(ModelConfig, UUID(config_id))
    if config:
        config.name = model_config_update.name
        config.provider = model_config_update.provider
        config.model_name = model_config_update.model_name
        config.base_url = model_config_update.base_url
        config.api_key = model_config_update.api_key
        config.max_tokens = model_config_update.max_tokens
        config.temperature = model_config_update.temperature
        config.top_p = model_config_update.top_p
        config.presence_penalty = model_config_update.presence_penalty
        config.frequency_penalty = model_config_update.frequency_penalty
        await db_session.commit()


async def delete_model_config(db_session: AsyncDbSession, config_id: str) -> None:
    db_config = await db_session.get(ModelConfig, UUID(config_id))
    if db_config:
        await db_session.delete(db_config)
        await db_session.commit()
