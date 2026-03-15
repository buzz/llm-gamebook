## Context

**Current State:**
- No user settings storage exists
- SQLite/SQLModel stack in use for other models

**Constraints:**
- Single-user system, no authentication required
- No new dependencies allowed
- Single settings record for the app

## Goals / Non-Goals

**Goals:**
- Store user settings (chat_view, enter_submits_message) server-side in SQLite
- Provide REST API for settings CRUD
- Automatic settings creation with defaults
- Minimal code changes

**Non-Goals:**
- User authentication (not applicable for single-user system)
- Settings versioning or history
- Multi-user support

## Decisions

**1. Database Schema: Single row for single user**
- *Decision:* Use `id` as primary key with fixed value (e.g., "settings") or auto-increment with single-row constraint
- *Rationale:* One-to-one relationship, efficient join, no duplicate settings possible
- *Alternative considered:* Separate settings_id column (unnecessary overhead)

**2. Default values in application code**
- *Decision:* Generate defaults in API when settings don't exist
- *Rationale:* Simpler than database defaults, easier to change defaults later
- *Alternative considered:* Database DEFAULT values (less flexible)

**3. PUT for upsert**
- *Decision:* Use PUT (not POST/PATCH) for settings endpoint
- *Rationale:* Idempotent, standard REST pattern for "resource at known location"
- *Alternative considered:* POST with separate create/update endpoints (overly complex)

**4. No partial updates**
- *Decision:* Require full settings object on PUT
- *Rationale:* Simpler implementation, avoids merge conflicts
- *Alternative considered:* PATCH with partial updates (adds complexity)

**5. Settings model in backend package**
- *Decision:* Add `UserSettings` to existing models package
- *Rationale:* Follows existing pattern (e.g., `ModelConfig`)
- *Alternative considered:* Separate settings package (premature)

## Risks / Trade-offs

**[Migration for existing users]** First access creates settings automatically
→ *Mitigation:* Create settings on first access with defaults, no migration script needed

**[Race condition on first access]** Multiple simultaneous requests for new user
→ *Mitigation:* Database unique constraint prevents duplicates, app handles integrity error

**[No settings validation]** API accepts any values for chat_view
→ *Mitigation:* Frontend controls available options, can add backend validation later if needed

**[No settings history]** Cannot track settings changes over time
→ *Mitigation:* Out of scope, can add later if needed

## Migration Plan

**Deployment:**
1. Deploy backend with new `UserSettings` model
2. No database migration needed (table created on first access via SQLModel)

**Rollback:**
- Backend rollback: API returns 404 for settings
- No data loss (settings are app preferences)

## Open Questions

1. Should settings be cached in memory for performance?
2. Should settings be synced via WebSocket for real-time changes?
3. Need to define valid values for `chat_view` ('standard', 'details', 'debug') - hardcode or config?
