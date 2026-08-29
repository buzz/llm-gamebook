from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine, create_async_engine
from sqlmodel import SQLModel, text

from llm_gamebook.constants import PROJECT_NAME, USER_DATA_PATH
from llm_gamebook.logger import logger

log = logger.getChild("database")


@asynccontextmanager
async def create_async_db_engine() -> AsyncIterator[AsyncEngine]:
    # Make sure all models are imported
    from .models import (  # noqa: F401, PLC0415
        Message,
        ModelConfig,
        Part,
        Session,
        Usage,
        UserSettings,
    )

    sqlite_file_name = f"{PROJECT_NAME}.db"
    sqlite_database_path = USER_DATA_PATH / sqlite_file_name
    sqlite_url = f"sqlite+aiosqlite:///{sqlite_database_path}"

    log_verb = "Using" if sqlite_database_path.exists() else "Creating"
    log.info("%s database '%s'", log_verb, sqlite_database_path)

    try:
        db_engine = create_async_engine(sqlite_url)
        await _create_db_and_tables(db_engine)
        yield db_engine
    finally:
        log.info("Shutting down database engine…")
        await db_engine.dispose()


async def _create_db_and_tables(db_engine: AsyncEngine) -> None:
    async with db_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
        await _migrate_session_table(conn)
        # Enable foreign key support in SQLite
        await conn.execute(text("PRAGMA foreign_keys=ON"))


async def _migrate_session_table(conn: AsyncConnection) -> None:
    """Add columns to the session table that older databases may lack.

    SQLite's create_all does not alter existing tables, so columns added in
    later versions are created manually here.
    """
    result = await conn.execute(text("PRAGMA table_info(session)"))
    existing_columns = {row[1] for row in result.all()}
    for column_name, column_type in (("ended_at", "DATETIME"), ("state", "JSON")):
        if column_name not in existing_columns:
            await conn.execute(text(f"ALTER TABLE session ADD COLUMN {column_name} {column_type}"))
            log.info("Added missing column '%s' to 'session' table", column_name)
