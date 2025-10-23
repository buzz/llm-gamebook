from dataclasses import dataclass
from pathlib import Path
from typing import Annotated, cast

import typer


@dataclass
class ContextState:
    debug: bool
    log_file: Path | None


app = typer.Typer()


@app.callback()
def state(
    ctx: typer.Context,
    *,
    debug: Annotated[bool, typer.Option(help="Enable debug logging.")] = False,
    log_file: Annotated[Path | None, typer.Option(help="Log to file")] = None,
) -> None:
    ctx.ensure_object(dict)
    ctx.obj["state"] = ContextState(debug, log_file)


@app.command()
def web(ctx: typer.Context) -> None:
    """Run web application."""
    import uvicorn  # noqa: PLC0415

    from llm_gamebook.web.app import create_app  # noqa: PLC0415

    state = cast("ContextState", ctx.obj["state"])
    uvicorn.run(create_app(state.log_file, debug=state.debug))


async def run_tui(log_file: Path | None, *, debug: bool) -> None:
    pass
    # from llm_gamebook.tui import TuiApp

    # tui_app = TuiApp(debug=debug)
    # tui_task = tui_app.run_async()

    # await asyncio.sleep(1)

    # engine = StoryEngine(model, state, tui_app)
    # engine_task = engine.run()

    # for result in await asyncio.gather(tui_task, engine_task, return_exceptions=True):
    #     if isinstance(result, Exception):
    #         logger.exception("Exception", exc_info=result)
    #         raise typer.Exit(-1)


@app.command()
def tui(ctx: typer.Context) -> None:
    """Run the terminal user interface."""
    # state = cast("ContextState", ctx.obj["state"])
    # asyncio.run(run_tui(state.story_state, debug=state.debug))


if __name__ == "__main__":
    app()
