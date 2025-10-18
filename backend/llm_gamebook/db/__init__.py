from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel import SQLModel

from llm_gamebook.db.chat import Chat  # noqa: F401
from llm_gamebook.db.message import Message  # noqa: F401

sqlite_file_name = "database.db"
sqlite_url = f"sqlite+aiosqlite:///{sqlite_file_name}"

db_engine = create_async_engine(sqlite_url, echo=True)


async def create_db_and_tables() -> None:
    async with db_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
