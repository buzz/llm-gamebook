from collections.abc import Sequence
from typing import TypedDict, Unpack
from uuid import UUID

from sqlmodel import func, select
from sqlmodel.ext.asyncio.session import AsyncSession as AsyncDbSession

from llm_gamebook.db.models import ModelConfig
from llm_gamebook.providers import ModelProvider


async def create_model_config(db_session: AsyncDbSession, config: ModelConfig) -> ModelConfig:
    db_session.add(config)
    await db_session.commit()
    await db_session.refresh(config)
    return config


async def get_model_configs(
    db_session: AsyncDbSession, skip: int = 0, limit: int = 100
) -> Sequence[ModelConfig]:
    stmt = select(ModelConfig).offset(skip).limit(limit)
    result = await db_session.exec(stmt)
    return result.all()


async def get_model_config_count(db_session: AsyncDbSession) -> int:
    stmt = select(func.count()).select_from(ModelConfig)
    result = await db_session.exec(stmt)
    return result.one()


async def get_model_config(db_session: AsyncDbSession, config_id: UUID) -> ModelConfig | None:
    return await db_session.get(ModelConfig, config_id)


class ModelConfigUpdate(TypedDict):
    config_id: UUID
    name: str
    provider: ModelProvider
    model_name: str
    base_url: str | None
    api_key: str | None
    context_window: int
    max_tokens: int
    temperature: float
    top_p: float
    presence_penalty: float
    frequency_penalty: float


async def update_model_config(
    db_session: AsyncDbSession, /, **kwargs: Unpack[ModelConfigUpdate]
) -> None:
    config = await db_session.get(ModelConfig, kwargs["config_id"])
    if config:
        config.name = kwargs["name"]
        config.provider = kwargs["provider"]
        config.model_name = kwargs["model_name"]
        config.base_url = kwargs["base_url"]
        config.api_key = kwargs["api_key"]
        config.context_window = kwargs["context_window"]
        config.max_tokens = kwargs["max_tokens"]
        config.temperature = kwargs["temperature"]
        config.top_p = kwargs["top_p"]
        config.presence_penalty = kwargs["presence_penalty"]
        config.frequency_penalty = kwargs["frequency_penalty"]
        await db_session.commit()


async def delete_model_config(db_session: AsyncDbSession, config_id: str) -> None:
    db_config = await db_session.get(ModelConfig, UUID(config_id))
    if db_config:
        await db_session.delete(db_config)
        await db_session.commit()
