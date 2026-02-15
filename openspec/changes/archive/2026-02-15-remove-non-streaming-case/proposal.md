## Why

The non-streaming code path in `StoryEngine.generate_response()` is dead code in production. The WebSocket handler always uses streaming, and the REST API doesn't call the agent at all. This unused branch contains a TODO for "recording durations" that would require complex graph iteration to solve - but if we remove the non-streaming case entirely, the TODO becomes moot. Simplifying now reduces maintenance burden and removes the need to implement duration tracking for non-streaming.

## What Changes

- Remove the `streaming` parameter from `StoryEngine.generate_response()` - always use streaming internally
- Remove the non-streaming `else` branch in `engine.py` (lines 81-86)
- Update test file `test_engine.py` to not pass the removed `streaming` parameter
- Update test file `test_story_flow.py` (broken_bulb) to not pass the removed `streaming` parameter
- Simplify `SessionAdapter.append_messages()` - the overload for optional IDs/durations can be cleaned up since non-streaming won't call it

## Capabilities

### New Capabilities
(none)

### Modified Capabilities
(none - the existing `thinking-duration` spec requirements remain satisfied; we're just simplifying implementation by removing the code path that lacked duration tracking)

## Impact

**Backend:**
- `llm_gamebook/engine/engine.py`: Remove ~10 lines of dead code
- `llm_gamebook/engine/session_adapter.py`: Simplify `append_messages()` signature
- `tests/llm_gamebook/engine/test_engine.py`: Update 7 test calls
- `tests/broken_bulb/test_story_flow.py`: Update 3 test calls

**No frontend impact** - the frontend already uses WebSocket streaming only.
