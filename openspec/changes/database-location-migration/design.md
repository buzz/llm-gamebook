## Context

**Current state:**
- SQLite database stored at `backend/database.db` (project-local)
- Database mixed with application code in version control
- No platform-standard user data directory usage

**Target state:**
- Database moved to platform-standard user data directory
- Linux: `~/.local/share/llm-gamebook/llm-gamebook.db`
- macOS: `~/Library/Application Support/llm-gamebook/llm-gamebook.db`
- Windows: `%APPDATA%\llm-gamebook\llm-gamebook.db`

**Constraints:**
- Must work across Linux, macOS, and Windows
- Early development stage - hard cut acceptable for existing users
- No migration needed for existing database

## Goals / Non-Goals

**Goals:**
- Separate application code from user data
- Follow OS conventions for application data storage
- Enable cleaner project structure and easier backups
- Support potential distribution/packaging

**Non-Goals:**
- Database migration from old location (users must manually migrate if needed)
- Sync/backup functionality for user data
- Multi-user support beyond OS user accounts

## Decisions

**1. Use platformdirs library**
- Rationale: Actively maintained, cross-platform, used by many popular Python packages
- Alternative considered: `appdirs` (less actively maintained)

**2. Auto-create user data directory**
- Rationale: Better UX than expecting users to create directory manually
- Implementation: Create in `lifespan()` startup with explicit error handling

**3. Keep example project path separate**
- Rationale: Examples are development assets, not user data
- Decision: Keep as-is (user manually clones to expected location)

**4. New database filename: `llm-gamebook.db`**
- Rationale: More specific than generic `database.db`
- Avoids confusion with other potential databases

## Risks / Trade-offs

**[Data loss for existing users]** → Hard cut acceptable (early development), document manual migration path

**[Directory creation failure]** → Explicit error handling in lifespan with clear error message

**[Permission issues]** → Let OS handle; clear error if directory cannot be created

## Migration Plan

**Deployment:**
1. Add `platformdirs` dependency
2. Update constants and database path
3. Implement directory creation in lifespan
4. Test on all platforms
5. Update documentation

**Rollback:**
None
