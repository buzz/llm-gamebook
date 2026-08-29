# Database Location

## Purpose

Stores the SQLite database in the platform-standard user data directory instead of the project directory, separating application code from user data, and auto-creates the directory on first run.

## Requirements

### Requirement: Database in user data directory

The SQLite database MUST be stored in the user data directory instead of the project directory.

#### Scenario: Database path

- **WHEN** the database engine is created
- **THEN** the database file must be located at `USER_DATA_DIR / "llm-gamebook.db"`
- **AND** the connection URL must use `sqlite+aiosqlite` protocol

#### Scenario: Automatic directory creation

- **WHEN** the database engine initializes
- **THEN** the `USER_DATA_DIR` directory must be created if it does not exist
- **AND** if creation fails, an explicit error must be raised before database initialization
