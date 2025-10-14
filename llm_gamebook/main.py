import asyncio
import logging
import os
import sys
from pathlib import Path

from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider

from llm_gamebook.engine import StoryEngine
from llm_gamebook.logger import logger
from llm_gamebook.story.state import Project, StoryState
from llm_gamebook.tui import TuiApp


async def main() -> int:
    debug = "--debug" in sys.argv
    streaming = "--no-streaming" not in sys.argv

    if debug:
        logger.setLevel(logging.DEBUG)

    model_name = os.getenv("MODEL_NAME", "GLM-4.5-Air")
    base_url = os.getenv("BASE_URL", "http://localhost:5001/v1/")
    api_key = os.getenv("API_KEY", "123")

    if not base_url.endswith("/"):
        base_url = f"{base_url}/"

    provider = OpenAIProvider(base_url=base_url, api_key=api_key)
    model = OpenAIChatModel(model_name, provider=provider)
    project_path = Path(__file__).parent.parent / "examples" / "broken-bulb"
    project = Project.from_dir(project_path)
    state = StoryState(project)

    tui_app = TuiApp(debug=debug)
    tui_task = tui_app.run_async()

    await asyncio.sleep(1)

    engine = StoryEngine(model, state, tui_app, streaming=streaming)
    engine_task = engine.run()

    return_code = 0

    for result in await asyncio.gather(tui_task, engine_task, return_exceptions=True):
        if isinstance(result, Exception):
            logger.exception("Exception", exc_info=result)
            return_code = -1

    return return_code


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
