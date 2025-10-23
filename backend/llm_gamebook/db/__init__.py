from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel import SQLModel, text

from .models import Message, Part, Session, Usage  # noqa: F401

sqlite_file_name = "database.db"
sqlite_url = f"sqlite+aiosqlite:///{sqlite_file_name}"

db_engine = create_async_engine(sqlite_url)


async def create_db_and_tables() -> None:
    async with db_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
        # Enable foreign key support in SQLite
        await conn.execute(text("PRAGMA foreign_keys=ON"))
