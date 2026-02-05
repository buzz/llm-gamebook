import pytest
from llm_gamebook.engine.providers import GroqProvider, OllamaProvider, OpenAIProvider

from llm_gamebook.db.models import ModelConfig
from llm_gamebook.web.model_factory import create_model_from_db_config


def test_create_model_openai() -> None:
    model = ModelConfig(
        name="OpenAI GPT-4",
        provider="openai",
        model_name="gpt-4",
        base_url="https://api.openai.com/v1",
        api_key="test-key",
    )
    result = create_model_from_db_config(model)
    assert result is not None
    assert isinstance(result, OpenAIProvider)


def test_create_model_ollama() -> None:
    model = ModelConfig(
        name="Ollama Llama3",
        provider="ollama",
        model_name="llama3",
        base_url="http://localhost:11434",
        api_key=None,
    )
    result = create_model_from_db_config(model)
    assert result is not None
    assert isinstance(result, OllamaProvider)


def test_create_model_groq() -> None:
    model = ModelConfig(
        name="Groq Llama3",
        provider="groq",
        model_name="llama-3.1-8b-instant",
        base_url="https://api.groq.com/openai/v1",
        api_key="test-key",
    )
    result = create_model_from_db_config(model)
    assert result is not None
    assert isinstance(result, GroqProvider)


def test_create_model_with_settings() -> None:
    model = ModelConfig(
        name="OpenAI with settings",
        provider="openai",
        model_name="gpt-4",
        base_url="https://api.openai.com/v1",
        api_key="test-key",
    )
    result = create_model_from_db_config(model)
    assert result is not None


def test_create_model_unsupported_provider() -> None:
    model = ModelConfig(
        name="Unknown Provider",
        provider="unknown",
        model_name="model-x",
        base_url="https://api.example.com",
        api_key="test-key",
    )
    with pytest.raises(ValueError, match="Unsupported provider"):
        create_model_from_db_config(model)
