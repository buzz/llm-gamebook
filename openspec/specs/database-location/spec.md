# Database Location

## ADDED Requirements

### Requirement: Database in user data directory

The SQLite database must be stored in the user data directory instead of the project directory.

#### Scenario: Database path

- **WHEN** the database engine is created
- **THEN** the database file must be located at `USER_DATA_DIR / "llm-gamebook.db"`
- **AND** the connection URL must use `sqlite+aiosqlite` protocol

#### Scenario: Automatic directory creation

- **WHEN** the database engine initializes
- **THEN** the `USER_DATA_DIR` directory must be created if it does not exist
- **AND** if creation fails, an explicit error must be raised before database initialization

## Implementation Details

### File: `backend/llm_gamebook/db/create_db.py`

```python
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel import SQLModel, text

from .models import ModelConfig, Message, Part, Session, Usage  # noqa: F401
from ..constants import USER_DATA_DIR

sqlite_file_name = "llm-gamebook.db"
sqlite_url = f"sqlite+aiosqlite:///{USER_DATA_DIR / sqlite_file_name}"

db_engine = create_async_engine(sqlite_url)
```

## Migration Notes

- **No migration needed**: Early development stage, hard cut acceptable
- **Existing users**: Will need to manually move `backend/database.db` if they have existing data
