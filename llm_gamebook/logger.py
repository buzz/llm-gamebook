import logging
from typing import Final

from colorama import Fore, Style


class ColorFormatter(logging.Formatter):
    COLORS: Final = {
        "WARNING": Fore.RED,
        "ERROR": Fore.RED,
        "DEBUG": Fore.CYAN,
        "INFO": Fore.GREEN,
        "CRITICAL": Fore.RED,
    }

    def format(self, record: logging.LogRecord) -> str:
        color = self.COLORS.get(record.levelname, "")
        if color:
            record.name = color + record.name
            record.levelname = color + record.levelname
            record.msg = color + record.msg
        return super().format(record) + Style.RESET_ALL


class ColorLogger(logging.Logger):
    def __init__(self, name: str) -> None:
        super().__init__(name)
        self.propagate = False
        color_formatter = ColorFormatter("%(name)-10s %(levelname)-18s %(message)s")
        console = logging.StreamHandler()
        console.setFormatter(color_formatter)
        self.addHandler(console)


logging.setLoggerClass(ColorLogger)
logger = logging.getLogger("llm-gamebook")
