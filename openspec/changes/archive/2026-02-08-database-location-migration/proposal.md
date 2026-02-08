## Why

Move SQLite database from `backend/database.db` (project-local) to user state directory to separate application code from user data, following OS conventions for application data storage.

## What Changes

- Add `platformdirs` dependency for cross-platform user directory detection
- Update database path from `backend/database.db` to platform-standard user data directory (`~/.local/share/llm-gamebook/llm-gamebook.db` on Linux)
- Auto-create user data directory on first run

## Capabilities

### New Capabilities
- `user-data-directory`: Cross-platform user data directory management using platformdirs library
- `database-location-migration`: Database stored in user state directory instead of project directory

### Modified Capabilities
- `examples`: Example project path handling needs to be updated to work with new directory structure

## Impact

**Affected code:**
- `backend/llm_gamebook/db/create_db.py` - Update database path
- `backend/pyproject.toml` - Add platformdirs dependency

**Dependencies:**
- New: `platformdirs>=4.0.0`

**Breaking changes:** Datebase location changes (okay as we're still in early development stage)
