## Why

Currently, user settings are not persisted server-side. As a single-user local web app, settings should persist across browser sessions and server restarts. This change adds server-side settings storage using SQLite.

## What Changes

- Add `UserSettings` model to store preferences in SQLite (single row for single user)
- Create `/settings` API endpoints (GET/PUT) for CRUD operations
- Settings stored server-side: `chat_view`, `enter_submits_message`

## Capabilities

### New Capabilities
- `user-settings`: User settings model with SQLite persistence and API endpoints for GET/PUT

### Modified Capabilities
None

## Impact

**Backend:**
- New model: `UserSettings` (SQLModel) with fields: id, chat_view, enter_submits_message
- New endpoints: `GET /settings`, `PUT /settings` in `backend/llm_gamebook/web/api/settings_router.py`
- Database table auto-created (no migration needed)
- No authentication required (single-user system)
