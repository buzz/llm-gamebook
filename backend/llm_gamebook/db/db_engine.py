from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlmodel import SQLModel, text

from llm_gamebook.constants import PROJECT_NAME, USER_DATA_DIR
from llm_gamebook.logger import logger

log = logger.getChild("database")


@asynccontextmanager
async def create_async_db_engine() -> AsyncIterator[AsyncEngine]:

    # Make sure all models are imported
    from .models import Message, ModelConfig, Part, Session, Usage  # noqa: F401, PLC0415

    sqlite_file_name = f"{PROJECT_NAME}.db"
    sqlite_url = f"sqlite+aiosqlite:///{USER_DATA_DIR / sqlite_file_name}"

    try:
        log.info("Creating database engine…")
        db_engine = create_async_engine(sqlite_url)
        await _create_db_and_tables(db_engine)
        yield db_engine
    finally:
        log.info("Shutting down database engine…")
        await db_engine.dispose()


async def _create_db_and_tables(db_engine: AsyncEngine) -> None:
    log.info("Creating database file and tables…")
    async with db_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
        # Enable foreign key support in SQLite
        await conn.execute(text("PRAGMA foreign_keys=ON"))
