from pathlib import Path

from pydantic_ai.models import Model
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.profiles.openai import OpenAIModelProfile
from pydantic_ai.providers.ollama import OllamaProvider
from pydantic_ai.providers.openai import OpenAIProvider

from llm_gamebook.story.project import Project
from llm_gamebook.story.state import StoryState


def get_model_state() -> tuple[Model, StoryState]:
    path = Path(Path.home() / "llm/llm-gamebook/llm-gamebook/examples/broken-bulb")
    state = StoryState(Project.from_path(path))

    # provider = OpenAIProvider(base_url="http://localhost:5001/v1", api_key="123")
    # model = OpenAIChatModel("Qwen3-30B-A3B-Thinking-2507", provider=provider)

    provider = OllamaProvider(base_url="http://localhost:5001/v1", api_key="123")
    model = OpenAIChatModel("Qwen3-30B-A3B-Thinking-2507", provider=provider)

    # provider = OllamaProvider(base_url="http://localhost:11434/v1", api_key="123")
    # model = OpenAIChatModel(
    #     "hf.co/unsloth/Qwen3-30B-A3B-Thinking-2507-GGUF:UD-Q4_K_XL", provider=provider
    # )

    return model, state
