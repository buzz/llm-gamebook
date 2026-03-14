from uuid import UUID

from pydantic import Field, RootModel

from llm_gamebook.providers import ModelProvider, ModelProviderList
from llm_gamebook.web.schemas.base import CamelCasedBaseModel


class BaseModelConfig(CamelCasedBaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    """User-friendly display name"""

    provider: ModelProvider
    """LLM provider type"""

    model_name: str = Field(..., min_length=1, max_length=255)
    """LLM model identifier"""

    base_url: str | None = Field(default=None, max_length=500)
    """Base URL for the provider API"""

    api_key: str | None = Field(default=None, max_length=1000)
    """API key for authentication"""

    context_window: int
    """Context windows length"""

    # Advanced parameters
    max_tokens: int
    temperature: float
    top_p: float
    presence_penalty: float
    frequency_penalty: float


class ModelConfigCreate(BaseModelConfig):
    pass


class ModelConfig(BaseModelConfig):
    """A model configuration."""

    id: UUID


class ModelConfigUpdate(BaseModelConfig):
    """Update fields for a model config."""


class ModelConfigs(CamelCasedBaseModel):
    """A list of LLM models."""

    data: list[ModelConfig]
    count: int


class ModelProviders(RootModel[ModelProviderList]):
    """A list of model providers."""
