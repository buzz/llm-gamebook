import asyncio
import logging
from pathlib import Path
from typing import Annotated

import typer
from pydantic_ai.models import Model
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider

from llm_gamebook.engine import StoryEngine
from llm_gamebook.logger import logger
from llm_gamebook.story.state import Project, StoryState
from llm_gamebook.tui import TuiApp

app = typer.Typer()


async def run_tui(model: Model, state: StoryState, *, debug: bool, streaming: bool) -> None:
    tui_app = TuiApp(debug=debug)
    tui_task = tui_app.run_async()

    await asyncio.sleep(1)

    engine = StoryEngine(model, state, tui_app, streaming=streaming)
    engine_task = engine.run()

    for result in await asyncio.gather(tui_task, engine_task, return_exceptions=True):
        if isinstance(result, Exception):
            logger.exception("Exception", exc_info=result)
            raise typer.Exit(-1)


@app.command()
def tui(  # noqa: PLR0913
    project_dir: Annotated[str, typer.Argument(help="Project directory")],
    model_name: Annotated[str, typer.Option(help="Model name", envvar="MODEL_NAME")] = "gpt-5-pro",
    base_url: Annotated[
        str | None,
        typer.Option(
            help="OpenAI compatible base URL (e.g. 'http://localhost:5001/v1')", envvar="BASE_URL"
        ),
    ] = None,
    api_key: Annotated[str | None, typer.Option(help="API key", envvar="OPENAI_API_KEY")] = None,
    *,
    debug: Annotated[bool, typer.Option(help="Enable debug logging.")] = False,
    streaming: Annotated[bool, typer.Option(help="Enable streaming responses.")] = True,
) -> None:
    """Run the terminal user interface."""
    if debug:
        logger.setLevel(logging.DEBUG)

    if isinstance(base_url, str) and not base_url.endswith("/"):
        base_url = f"{base_url}/"

    provider = OpenAIProvider(base_url=base_url, api_key=api_key)
    model = OpenAIChatModel(model_name, provider=provider)
    project = Project.from_path(Path(project_dir))
    state = StoryState(project)

    asyncio.run(run_tui(model, state, debug=debug, streaming=streaming))


if __name__ == "__main__":
    app()
