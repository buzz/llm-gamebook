import logging
from copy import copy
from pathlib import Path
from typing import Literal

import click
from uvicorn.logging import DefaultFormatter

from llm_gamebook.constants import PROJECT_NAME

logger = logging.getLogger(PROJECT_NAME)


class WebAppFormatter(DefaultFormatter):
    def formatMessage(self, record: logging.LogRecord) -> str:  # noqa: N802
        if not self.use_colors:
            return super().formatMessage(record)
        recordcopy = copy(record)
        recordcopy.name = click.style(recordcopy.name, fg="bright_white")
        return super().formatMessage(recordcopy)


def setup_logger(
    mode: Literal["web", "tui"], level: int, log_file: Path | None = None
) -> logging.Logger:
    """
    Configure console logging for the web UI.
    """
    if logger.hasHandlers():
        return logger  # already configured

    handler: logging.Handler

    if mode == "web":
        formatter = WebAppFormatter(r"%(levelprefix)s %(name)s %(message)s")
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(level)

        for name in logging.Logger.manager.loggerDict:
            if name.startswith("sqlalchemy"):
                other_logger = logging.getLogger(name)
                for handler in other_logger.handlers:
                    handler.setFormatter(formatter)

    elif mode == "tui" and log_file is None:
        # disable logging completely
        logger.addHandler(logging.NullHandler())
        logger.setLevel(logging.CRITICAL + 1)

    if log_file:
        handler = logging.FileHandler(log_file, mode="a", encoding="utf-8")
        handler.setFormatter(
            logging.Formatter(
                fmt="[{asctime}] {levelname:<8} {name}: {message}",
                style="{",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
        )
        logger.addHandler(handler)
        logger.setLevel(level)

    return logger
