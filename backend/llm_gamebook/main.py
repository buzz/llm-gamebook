import os
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
def web(
    ctx: typer.Context,
    *,
    host: Annotated[str, typer.Option(help="The host to serve on.")] = "127.0.0.1",
    port: Annotated[
        int, typer.Option(help="The port to serve on.", envvar="LLM_GAMEBOOK_PORT")
    ] = 8000,
    dev: Annotated[
        bool,
        typer.Option(
            help=(
                "Enable auto-reload and debug logs. "
                "This is [bold]resource intensive[/bold], use it only during development."
            ),
        ),
    ] = False,
) -> None:
    """Run web application."""
    import uvicorn  # noqa: PLC0415

    from llm_gamebook.web.app import create_app  # noqa: PLC0415

    state = cast("ContextState", ctx.obj["state"])

    if dev:
        # Pass options via env vars since uvicorn spawns a separate process
        if state.log_file:
            os.environ["LLM_GAMEBOOK_LOG_FILE"] = str(state.log_file)
        os.environ["LLM_GAMEBOOK_DEBUG"] = str(state.debug)

        reload_dir = str(Path(__file__).parent)

        # Need to use import string for reload
        uvicorn.run(
            "llm_gamebook.web.dev:app",
            host=host,
            port=port,
            reload=True,
            reload_dirs=reload_dir,
        )

    # Normal start-up
    else:
        app = create_app(state.log_file, debug=state.debug)
        uvicorn.run(app, host=host, port=port)


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
