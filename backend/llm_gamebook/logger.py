import logging

from llm_gamebook.constants import PROJECT_NAME

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[logging.FileHandler(f"{PROJECT_NAME}.log", mode="a", encoding="utf-8")],
)

logger = logging.getLogger(PROJECT_NAME)
