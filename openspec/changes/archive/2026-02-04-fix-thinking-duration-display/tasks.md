# Tasks

## Backend: Add duration_seconds to ThinkingPart

- [x] 1.1 Add duration_seconds field to ThinkingPart model in backend/api/models.py
- [x] 1.2 Add duration_seconds field to PartBase in db/models/part.py
- [x] 1.3 Track thinking start time in _StreamRunner and calculate duration
- [x] 1.4 Update Part.from_model_parts to extract duration from pydantic_ai ThinkingPart
- [x] 1.5 Regenerate OpenAPI schema

## Frontend: Update ThinkingPart display

- [x] 2.1 Update label condition to show persisted duration when deltaSecs is not available
- [x] 2.2 Update ThinkingPart.tsx with the new logic

## Verify

- [x] 3.1 Verify the button shows "Thought for X seconds" after streaming ends
- [x] 3.2 Verify duration persists when reloading a saved session
