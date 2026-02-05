from uuid import UUID

from fastapi import APIRouter, HTTPException

from llm_gamebook.db.crud.model_config import create_model_config as crud_create_model_config
from llm_gamebook.db.crud.model_config import delete_model_config as crud_delete_model_config
from llm_gamebook.db.crud.model_config import (
    get_model_config,
    get_model_config_count,
    get_model_configs,
)
from llm_gamebook.db.crud.model_config import update_model_config as crud_update_model_config
from llm_gamebook.db.models import ModelConfig as SqlModelModelConfig
from llm_gamebook.providers import PROVIDERS
from llm_gamebook.web.api.deps import DbSessionDep
from llm_gamebook.web.schemas.common import ServerMessage
from llm_gamebook.web.schemas.model_config import (
    ModelConfig,
    ModelConfigCreate,
    ModelConfigs,
    ModelConfigUpdate,
    ModelProviders,
)

model_config_router = APIRouter(prefix="/model-configs", tags=["model-configs"])


@model_config_router.get("/")
async def read_model_configs(
    db_session: DbSessionDep, skip: int = 0, limit: int = 100
) -> ModelConfigs:
    return ModelConfigs(
        data=[
            ModelConfig(**c.model_dump()) for c in await get_model_configs(db_session, skip, limit)
        ],
        count=await get_model_config_count(db_session),
    )


@model_config_router.get("/{config_id}", response_model=ModelConfig)
async def read_model_config(db_session: DbSessionDep, config_id: UUID) -> SqlModelModelConfig:
    config = await get_model_config(db_session, config_id)
    if not config:
        raise HTTPException(status_code=404, detail="LLM model not found")
    return config


@model_config_router.post("/", response_model=ModelConfig)
async def create_model_config(
    db_session: DbSessionDep, config_in: ModelConfigCreate
) -> SqlModelModelConfig:
    db_config = SqlModelModelConfig(**config_in.model_dump())
    return await crud_create_model_config(db_session, db_config)


@model_config_router.put("/{config_id}")
async def update_model_config(
    db_session: DbSessionDep, config_id: str, config_in: ModelConfigUpdate
) -> ServerMessage:
    await crud_update_model_config(db_session, config_id, config_in)
    return ServerMessage(message="Model config updated successfully.")


@model_config_router.delete("/{config_id}")
async def delete_model_config(db_session: DbSessionDep, config_id: str) -> ServerMessage:
    await crud_delete_model_config(db_session, config_id)
    return ServerMessage(message="Model config deleted successfully.")


@model_config_router.get("/providers/")
async def list_providers() -> ModelProviders:
    return ModelProviders(PROVIDERS)
