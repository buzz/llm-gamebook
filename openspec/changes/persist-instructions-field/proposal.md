## Why

Pydantic AI's `ModelRequest` already contains an `instructions` field, but our database `Message` model doesn't persist it. This means we lose important context when storing messages and the frontend can't access this data via the API. We need to persist this field for completeness and future UI features.

## What Changes

1. Add `instructions` field to the database `Message` model
2. Add `instructions` field to API schemas/DTOs
3. Regenerate frontend API types (`frontend/src/types/openapi.d.ts`)
4. Ensure the field is serialized in API responses

## Capabilities

### New Capabilities
- `message-instructions-field`: Persist the `instructions` field from Pydantic AI's `ModelRequest` to our database `Message` object and expose it via API

### Modified Capabilities
- None (existing specs remain unchanged)

## Impact

- **Database**: `backend/llm_gamebook/models/` - Add `instructions` column to `Message` model
- **API**: `backend/llm_gamebook/schemas/` - Add `instructions` field to message DTOs
- **Frontend**: Regenerate `frontend/src/types/openapi.d.ts`
- **No GUI changes** - Display will be handled in a separate change
