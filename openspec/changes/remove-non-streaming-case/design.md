## Context

The `StoryEngine.generate_response()` method currently has two code paths:
1. **Streaming** (when `streaming=True`): Uses `StreamRunner` to iterate the agent graph, track part IDs and durations, and stream updates to the client
2. **Non-streaming** (when `streaming=False`): Simply calls `agent.run()` and stores messages without any duration tracking

The non-streaming path is dead code:
- WebSocket handler always passes `streaming=True` 
- REST API doesn't call the agent at all
- All production traffic uses streaming

The non-streaming path has a TODO to "record durations for non-streaming, too" - but this would require using `agent.iter()` (the same as streaming) to get event-based timing, making the non-streaming path essentially equivalent to streaming.

## Goals / Non-Goals

**Goals:**
- Remove dead code from the codebase
- Simplify `generate_response()` to only one code path
- Remove the need to ever implement duration tracking for non-streaming

**Non-Goals:**
- No changes to streaming behavior (that works fine)
- No changes to the frontend (already uses WebSocket streaming only)
- No new features or capabilities

## Decisions

### Decision: Remove non-streaming entirely vs. implement it properly

**Chosen:** Remove entirely

**Rationale:**
- The non-streaming path has no production use
- Implementing proper duration tracking would require using `agent.iter()` anyway (same as streaming)
- Removing is simpler than fixing

### Decision: Keep `streaming` parameter vs. remove it entirely

**Chosen:** Remove the parameter entirely

**Rationale:**
- If there's only one code path, the parameter is unnecessary
- Simpler API: `generate_response(db_session)` vs `generate_response(db_session, streaming=True)`

## Risks / Trade-offs

**[Risk]** Tests that previously used non-streaming need updates
- **Mitigation**: Update test calls to remove the parameter entirely

**[Risk]** Someone might want non-streaming in the future for debugging
- **Mitigation**: The `StreamRunner` can be used directly if needed; removing the high-level parameter doesn't prevent that
