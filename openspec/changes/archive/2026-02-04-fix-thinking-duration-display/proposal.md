# Fix Thinking Duration Display

## Why

The `ThinkingPart` component shows a placeholder text `"Thought for TODO"` when streaming ends instead of displaying the actual thinking duration. This creates a poor user experience by leaving an obvious debug artifact visible to end users.

## What Changes

1. Backend: Add `duration_seconds` field to `ThinkingPart` model, track thinking time server-side
2. Frontend: Update `ThinkingPart` to display the persisted duration

## Capabilities

### New Capabilities
- `ThinkingPart` displays duration from backend when loading saved sessions

### Modified Capabilities
- `ThinkingPart` component button label: Shows "Thought for X seconds" instead of "Thought for TODO" when streaming completes

## Impact

- `backend/llm_gamebook/models/`: Add duration_seconds to ThinkingPart schema
- `frontend/src/components/Player/Messages/ThinkingPart.tsx`: Update label rendering logic
- `frontend/src/types/openapi.d.ts`: Regenerated with new field
