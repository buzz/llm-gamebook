import asyncio
import logging
import sys
from pathlib import Path

from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider

from llm_gamebook.engine import StoryContext, StoryEngine
from llm_gamebook.logger import logger
from llm_gamebook.story.loader import YAMLLoader

if __name__ == "__main__":
    if "--debug" in sys.argv:
        logger.setLevel(logging.DEBUG)

    model = OpenAIModel(
        "models/gguf/Qwen3-32B-Q4_K_M.gguf",
        provider=OpenAIProvider(base_url="http://localhost:5001/v1/", api_key="123"),
    )
    state = YAMLLoader(Path(__file__).parent.parent / "examples" / "broken-bulb").load()
    context = StoryContext(state)
    engine = StoryEngine(model, context)
    asyncio.run(engine.story_loop())
