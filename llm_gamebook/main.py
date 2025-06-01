import asyncio
import logging
import sys
from pathlib import Path

from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider

from llm_gamebook.engine import StoryEngine
from llm_gamebook.engine.tui import TextUserInterface
from llm_gamebook.logger import logger
from llm_gamebook.story.state import Project, StoryState

if __name__ == "__main__":
    debug = "--debug" in sys.argv
    streaming = "--no-streaming" not in sys.argv

    if debug:
        logger.setLevel(logging.DEBUG)

    model = OpenAIModel(
        "models/gguf/Qwen3-32B-Q4_K_M.gguf",
        provider=OpenAIProvider(base_url="http://localhost:5001/v1/", api_key="123"),
    )
    project_path = Path(__file__).parent.parent / "examples" / "broken-bulb"
    project = Project.from_dir(project_path)
    state = StoryState(project)
    engine = StoryEngine(model, state, TextUserInterface(debug=debug), streaming=streaming)
    asyncio.run(engine.story_loop())
