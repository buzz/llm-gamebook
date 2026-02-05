import enum
from dataclasses import dataclass
from typing import Final


class ModelProvider(enum.StrEnum):
    ANTHROPIC = "anthropic"
    DEEPSEEK = "deepseek"
    GOOGLE = "google"
    MISTRAL = "mistral"
    OLLAMA = "ollama"
    OPENAI = "openai"
    OPENAI_COMPATIBLE = "openai-compatible"
    OPENROUTER = "openrouter"
    XAI = "xai"


@dataclass
class ModelProviderInfo:
    """Model provider information."""

    label: str
    supports_base_url: bool
    supports_max_tokens: bool
    supports_temperature: bool
    supports_top_p: bool
    supports_presence_penalty: bool
    supports_frequency_penalty: bool
    supports_logit_bias: bool
    supports_extra_headers: bool
    supports_extra_body: bool
    default_base_url: str | None = None


type ModelProviderList = dict[ModelProvider, ModelProviderInfo]


PROVIDERS: Final[ModelProviderList] = {
    ModelProvider.ANTHROPIC: ModelProviderInfo(
        label="Anthropic",
        supports_base_url=True,
        supports_max_tokens=True,
        supports_temperature=True,
        supports_top_p=True,
        supports_presence_penalty=False,
        supports_frequency_penalty=False,
        supports_logit_bias=False,
        supports_extra_headers=True,
        supports_extra_body=True,
        default_base_url="https://api.anthropic.com",
    ),
    ModelProvider.DEEPSEEK: ModelProviderInfo(
        label="DeepSeek",
        supports_base_url=True,
        supports_max_tokens=True,
        supports_temperature=True,
        supports_top_p=True,
        supports_presence_penalty=True,
        supports_frequency_penalty=True,
        supports_logit_bias=True,
        supports_extra_headers=True,
        supports_extra_body=True,
        default_base_url="https://api.deepseek.com/v1",
    ),
    ModelProvider.GOOGLE: ModelProviderInfo(
        label="Google",
        supports_base_url=True,
        supports_max_tokens=True,
        supports_temperature=True,
        supports_top_p=True,
        supports_presence_penalty=True,
        supports_frequency_penalty=True,
        supports_logit_bias=False,
        supports_extra_headers=False,
        supports_extra_body=False,
        default_base_url="https://aiplatform.googleapis.com",
    ),
    ModelProvider.MISTRAL: ModelProviderInfo(
        label="Mistral",
        supports_base_url=False,
        supports_max_tokens=True,
        supports_temperature=True,
        supports_top_p=True,
        supports_presence_penalty=True,
        supports_frequency_penalty=True,
        supports_logit_bias=False,
        supports_extra_headers=False,
        supports_extra_body=False,
    ),
    ModelProvider.OLLAMA: ModelProviderInfo(
        label="Ollama",
        supports_base_url=True,
        supports_max_tokens=True,
        supports_temperature=True,
        supports_top_p=True,
        supports_presence_penalty=True,
        supports_frequency_penalty=True,
        supports_logit_bias=True,
        supports_extra_headers=True,
        supports_extra_body=True,
        default_base_url="http://localhost:11434/v1",
    ),
    ModelProvider.OPENAI: ModelProviderInfo(
        label="OpenAI",
        supports_base_url=False,
        supports_max_tokens=True,
        supports_temperature=True,
        supports_top_p=True,
        supports_presence_penalty=True,
        supports_frequency_penalty=True,
        supports_logit_bias=True,
        supports_extra_headers=True,
        supports_extra_body=True,
        default_base_url="https://api.openai.com/v1",
    ),
    ModelProvider.OPENAI_COMPATIBLE: ModelProviderInfo(
        label="OpenAI-compatible API",
        supports_base_url=True,
        supports_max_tokens=True,
        supports_temperature=True,
        supports_top_p=True,
        supports_presence_penalty=True,
        supports_frequency_penalty=True,
        supports_logit_bias=True,
        supports_extra_headers=True,
        supports_extra_body=True,
        default_base_url="http://localhost:8000/v1",
    ),
    ModelProvider.OPENROUTER: ModelProviderInfo(
        label="OpenRouter",
        supports_base_url=True,
        supports_max_tokens=True,
        supports_temperature=True,
        supports_top_p=True,
        supports_presence_penalty=True,
        supports_frequency_penalty=True,
        supports_logit_bias=True,
        supports_extra_headers=True,
        supports_extra_body=True,
        default_base_url="https://openrouter.ai/api/v1",
    ),
    ModelProvider.XAI: ModelProviderInfo(
        label="xAI",
        supports_base_url=False,
        supports_max_tokens=True,
        supports_temperature=True,
        supports_top_p=True,
        supports_presence_penalty=True,
        supports_frequency_penalty=True,
        supports_logit_bias=False,
        supports_extra_headers=True,
        supports_extra_body=False,
    ),
}
