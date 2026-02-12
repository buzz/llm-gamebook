## Overview

Persist Pydantic AI's `instructions` field from `ModelRequest` to our database `Message` object and expose it via the API.

## Technical Approach

### Database Layer

Add `instructions` column to the `Message` SQLAlchemy model:

```python
# backend/llm_gamebook/db/models/message.py
class Message(Base):
    # ... existing fields ...
    instructions: Mapped[str | None] = mapped_column(String, nullable=True)
```

### API Layer

Add `instructions` field to message response schemas:

```python
# backend/llm_gamebook/schemas/message.py
class MessageResponse(BaseModel):
    id: UUID
    instructions: str | None = None
    # ... other fields ...
```

### Frontend Layer

Regenerate API types:

```bash
cd frontend && pnpm generate-api-types
```

This will update `frontend/src/types/openapi.d.ts` to include `instructions` on message types.

## Data Flow

1. Pydantic AI creates `ModelRequest` with `instructions` field
2. Engine extracts `instructions` when creating/saving `Message`
3. `Message` model persists `instructions` to database
4. API response includes `instructions` field
5. Frontend types reflect the field (for future UI use)

## Key Considerations

- Field is nullable since not all messages will have instructions
- No changes to GUI - field is just persisted and typed
- Frontend types regenerate automatically from OpenAPI spec
