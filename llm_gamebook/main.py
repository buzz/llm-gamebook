import asyncio
import logging
import sys

from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider

from llm_gamebook.engine import GameEngine
from llm_gamebook.logger import logger

if __name__ == "__main__":
    if "--debug" in sys.argv:
        logger.setLevel(logging.DEBUG)

    model = OpenAIModel(
        "models/gguf/Qwen3-32B-Q4_K_M.gguf",
        provider=OpenAIProvider(base_url="http://localhost:5001/v1/", api_key="123"),
    )
    engine = GameEngine(model)
    asyncio.run(engine.game_loop())
