# Design: Fix Thinking Duration Display

## Context

The `ThinkingPart` component tracks thinking duration using:
- `mountTime` ref: Records when streaming started (client-side only)
- `deltaSecs` state: Stores elapsed seconds, updated every second (client-side only)
- `isStreaming` prop: Indicates if currently streaming

**Current problems:**
1. Label bug: When streaming ends, `isStreaming` becomes false, causing fallback to `'Thought for TODO'`
2. No persistence: Duration is not tracked server-side, so reloading a session shows no duration

### Backend Architecture

**Message flow:**
```
pydantic_ai ThinkingPart → _StreamRunner → SessionAdapter.append_messages → Part.from_model_parts → DB
```

**Key files to modify:**
- `llm_gamebook/web/api/models.py`: Add `duration_seconds` to `ThinkingPart`
- `llm_gamebook/db/models/part.py`: Add `duration_seconds` to `PartBase`
- `llm_gamebook/engine/engine.py`: Track thinking duration in `_StreamRunner`

### Backend Schema

Current `ThinkingPart` schema (api/models.py):
```python
class ThinkingPart(BaseModel):
    id: UUID
    part_kind: Literal["thinking"] = "thinking"
    content: str
    provider_name: str | None = None
```

Need to add:
```python
    duration_seconds: int | None = None
    """Duration of the thinking in seconds."""
```

The backend tracks thinking start time in `_StreamRunner` and calculates duration when the thinking part ends.

## Goals / Non-Goals

**Goals:**
- Persist thinking duration server-side
- Display actual thinking duration in the button label
- Never show placeholder text to users

**Non-Goals:**
- Change the streaming indicator ("Thinking for X seconds…")
- Modify the component's timing logic (live updates during streaming)

## Decisions

### Decision 1: Backend schema change

Add `duration_seconds: int | None` to `ThinkingPart` model. The backend tracks timing when creating thinking parts.

### Decision 2: Frontend rendering approach

Display duration from backend when available. Use client-side tracking only for live updates during streaming.

```typescript
const label = deltaSecs !== null
  ? (isStreaming
    ? `Thinking for ${deltaSecs.toString()} seconds…`
    : `Thought for ${deltaSecs.toString()} seconds`)
  : (part.duration_seconds !== null
    ? `Thought for ${part.duration_seconds.toString()} seconds`
    : 'Thought for TODO')
```

This approach:
- Prioritizes client-side deltaSecs (live updates during streaming)
- Falls back to persisted duration_seconds when available
- Only shows placeholder if both tracking methods failed
