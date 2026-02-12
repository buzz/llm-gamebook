from unittest.mock import MagicMock

import pytest
from pydantic_ai.models import Model
from pydantic_ai.models.anthropic import AnthropicModel
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.models.openrouter import OpenRouterModel
from pydantic_ai.models.xai import XaiModel

from llm_gamebook.engine._model_factory import _get_logging_http_client, create_model_from_db_config
from llm_gamebook.providers import ModelProvider


def test_create_model_anthropic() -> None:
    model = create_model_from_db_config(
        model_name="claude-sonnet-4-20250514",
        provider=ModelProvider.ANTHROPIC,
        base_url="https://api.anthropic.com",
        api_key="test-key",
    )
    assert isinstance(model, AnthropicModel)


def test_create_model_deepseek() -> None:
    model = create_model_from_db_config(
        model_name="deepseek-chat",
        provider=ModelProvider.DEEPSEEK,
        base_url=None,
        api_key="test-key",
    )
    assert isinstance(model, OpenAIChatModel)


def test_create_model_google() -> None:
    model = create_model_from_db_config(
        model_name="gemini-2.0-flash-exp",
        provider=ModelProvider.GOOGLE,
        base_url="https://aiplatform.googleapis.com",
        api_key="test-key",
    )
    assert isinstance(model, Model)


def test_create_model_mistral() -> None:
    model = create_model_from_db_config(
        model_name="mistral-large-latest",
        provider=ModelProvider.MISTRAL,
        base_url=None,
        api_key="test-key",
    )
    assert isinstance(model, Model)


def test_create_model_ollama() -> None:
    model = create_model_from_db_config(
        model_name="llama3.2",
        provider=ModelProvider.OLLAMA,
        base_url="http://localhost:11434/v1",
        api_key=None,
    )
    assert isinstance(model, OpenAIChatModel)


def test_create_model_openai_compatible() -> None:
    model = create_model_from_db_config(
        model_name="custom-model",
        provider=ModelProvider.OPENAI_COMPATIBLE,
        base_url="http://localhost:8000/v1",
        api_key="test-key",
    )
    assert isinstance(model, OpenAIChatModel)


def test_create_model_openai() -> None:
    model = create_model_from_db_config(
        model_name="gpt-4o",
        provider=ModelProvider.OPENAI,
        base_url=None,
        api_key="test-key",
    )
    assert isinstance(model, OpenAIChatModel)


def test_create_model_openrouter() -> None:
    model = create_model_from_db_config(
        model_name="anthropic/claude-sonnet-4-20250514",
        provider=ModelProvider.OPENROUTER,
        base_url=None,
        api_key="test-key",
    )
    assert isinstance(model, OpenRouterModel)


def test_create_model_xai_with_api_key() -> None:
    model = create_model_from_db_config(
        model_name="grok-beta",
        provider=ModelProvider.XAI,
        base_url=None,
        api_key="test-key",
    )
    assert isinstance(model, XaiModel)


def test_create_model_xai_without_api_key() -> None:
    with pytest.raises(ValueError, match=r"x\.AI needs API key"):
        create_model_from_db_config(
            model_name="grok-beta",
            provider=ModelProvider.XAI,
            base_url=None,
            api_key=None,
        )


def test_create_model_unsupported_provider() -> None:
    with pytest.raises(ValueError, match="Unsupported provider"):
        create_model_from_db_config(
            model_name="some-model",
            provider=MagicMock(spec=ModelProvider),
            base_url=None,
            api_key=None,
        )


def test_get_logging_http_client() -> None:
    http_client = _get_logging_http_client()
    assert http_client is not None
    assert http_client.timeout is not None
    assert "request" in http_client.event_hooks
