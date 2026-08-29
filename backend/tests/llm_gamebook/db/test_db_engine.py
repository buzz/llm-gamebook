"""Tests for database creation and the lightweight session table migration."""

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from llm_gamebook.db.db_engine import _create_db_and_tables
from llm_gamebook.db.models import (  # noqa: F401
    Message,
    ModelConfig,
    Part,
    Session,
    Usage,
    UserSettings,
)

LEGACY_SESSION_TABLE = (
    "CREATE TABLE session ("
    "id UUID PRIMARY KEY NOT NULL, "
    "timestamp DATETIME, "
    "title VARCHAR, "
    "project_id VARCHAR NOT NULL, "
    "config_id UUID"
    ")"
)


async def _create_legacy_db() -> AsyncEngine:
    """Create a database with the session table as it existed before Stage 5."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.execute(text(LEGACY_SESSION_TABLE))
    return engine


async def _session_columns(engine: AsyncEngine) -> set[str]:
    async with engine.connect() as conn:
        result = await conn.execute(text("PRAGMA table_info(session)"))
        return {row[1] for row in result.all()}


async def test_create_db_and_tables_migrates_legacy_session_table() -> None:
    """A legacy database is upgraded with the new session columns on startup."""
    engine = await _create_legacy_db()
    try:
        columns_before = await _session_columns(engine)
        assert "state" not in columns_before
        assert "ended_at" not in columns_before

        await _create_db_and_tables(engine)

        columns_after = await _session_columns(engine)
        assert "state" in columns_after
        assert "ended_at" in columns_after
    finally:
        await engine.dispose()


async def test_create_db_and_tables_is_idempotent_for_new_databases() -> None:
    """Running migrations on a fresh database is a no-op."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    try:
        await _create_db_and_tables(engine)
        await _create_db_and_tables(engine)

        columns = await _session_columns(engine)
        assert "state" in columns
        assert "ended_at" in columns
    finally:
        await engine.dispose()
