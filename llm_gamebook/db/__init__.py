from sqlmodel import SQLModel, create_engine

from llm_gamebook.db.chat import Chat  # noqa: F401
from llm_gamebook.db.message import Message  # noqa: F401

sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

engine = create_engine(sqlite_url, echo=True)


def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)
