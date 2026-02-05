import json

import httpx
from pydantic_ai.models import Model
from pydantic_ai.models.anthropic import AnthropicModel
from pydantic_ai.models.google import GoogleModel
from pydantic_ai.models.mistral import MistralModel
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.models.openrouter import OpenRouterModel
from pydantic_ai.models.xai import XaiModel
from pydantic_ai.providers.anthropic import AnthropicProvider
from pydantic_ai.providers.deepseek import DeepSeekProvider
from pydantic_ai.providers.google import GoogleProvider
from pydantic_ai.providers.mistral import MistralProvider
from pydantic_ai.providers.ollama import OllamaProvider
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.providers.openrouter import OpenRouterProvider
from pydantic_ai.providers.xai import XaiProvider

from llm_gamebook.logger import logger
from llm_gamebook.providers import ModelProvider


def _get_logging_http_client(timeout: float = 10.0, connect: float = 5.0) -> httpx.AsyncClient:
    async def log_request(request: httpx.Request) -> None:
        log = logger.getChild("http-request")
        if request.method.upper() == "POST":
            body = request.content
            try:
                body = json.loads(body)
            except ValueError:
                body_display = f"Couldn't decode json body: {body.decode()}"
            else:
                body_display = f"body:\n{json.dumps(body, indent=2)}"
            log.debug("POST %s body:\n%s", request.url, body_display)

    return httpx.AsyncClient(
        timeout=httpx.Timeout(timeout=timeout, connect=connect),
        event_hooks={"request": [log_request]},
    )


def create_model_from_db_config(
    model_name: str,
    provider: ModelProvider,
    base_url: str | None,
    api_key: str | None,
) -> Model:
    http_client = _get_logging_http_client()
    model: Model

    match provider:
        case ModelProvider.ANTHROPIC:
            an_prov = AnthropicProvider(base_url=base_url, api_key=api_key, http_client=http_client)
            model = AnthropicModel(model_name, provider=an_prov)

        case ModelProvider.DEEPSEEK:
            ds_prov = DeepSeekProvider(api_key=api_key, http_client=http_client)
            model = OpenAIChatModel(model_name, provider=ds_prov)

        case ModelProvider.GOOGLE:
            goog_prov = GoogleProvider(base_url=base_url, api_key=api_key, http_client=http_client)
            model = GoogleModel(model_name, provider=goog_prov)

        case ModelProvider.MISTRAL:
            mis_prov = MistralProvider(api_key=api_key, http_client=http_client)
            model = MistralModel(model_name, provider=mis_prov)

        case ModelProvider.OLLAMA:
            ollama_prov = OllamaProvider(base_url, api_key, http_client=http_client)
            model = OpenAIChatModel(model_name, provider=ollama_prov)

        case ModelProvider.OPENAI_COMPATIBLE:
            openai_prov = OpenAIProvider(base_url, api_key, http_client=http_client)
            model = OpenAIChatModel(model_name, provider=openai_prov)

        case ModelProvider.OPENAI:
            openai_prov = OpenAIProvider(api_key, http_client=http_client)
            model = OpenAIChatModel(model_name, provider=openai_prov)

        case ModelProvider.OPENROUTER:
            or_prov = OpenRouterProvider(api_key=api_key, http_client=http_client)
            model = OpenRouterModel(model_name, provider=or_prov)

        case ModelProvider.XAI:
            if not api_key:
                msg = "x.AI needs API key"
                raise ValueError(msg)
            xai_prov = XaiProvider(api_key=api_key)
            model = XaiModel(model_name, provider=xai_prov)

        case _:
            msg = f"Unsupported provider: {provider}"
            raise ValueError(msg)

    return model
