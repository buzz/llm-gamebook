# Capability: Persist Instructions Field on Message

## Purpose

Persist the `instructions` field from Pydantic AI's `ModelRequest` to the database `Message` object and expose it via the API for future frontend use.

## Requirements

### FR1: Database Schema
The `Message` SQLAlchemy model MUST include an `instructions` column:
- Type: `String` (or `Text`)
- Nullable: `true`
- Default: `null`

### FR2: API Schema
The message response DTOs MUST include an `instructions` field:
- Type: `string` or `null`
- Optional: `true`
- Serialized in API responses

### FR3: TypeScript Types
The frontend OpenAPI types MUST include `instructions` on message types after running `pnpm generate-api-types`.

## Behavior

### Normal Flow
1. Pydantic AI creates `ModelRequest` containing `instructions`
2. Engine extracts `instructions` when creating `Message`
3. `Message.instructions` is set from the extracted value
4. Database persists the value
5. API responses include `instructions` field

### Edge Cases
- If `instructions` is `null`/`undefined` in `ModelRequest`, store `null`
- Existing messages without `instructions` have `null` value

## Out of Scope

- Displaying `instructions` in the GUI (separate change)
- Modifying message creation/retrieval logic beyond adding the field
