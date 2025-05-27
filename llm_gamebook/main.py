import asyncio
import logging
import sys

from llm_gamebook.engine import GameEngine
from llm_gamebook.logger import logger

if __name__ == "__main__":
    if "--debug" in sys.argv:
        logger.setLevel(logging.DEBUG)

    engine = GameEngine("http://localhost:5001/v1/")
    engine.example()
    asyncio.run(engine.game_loop())
