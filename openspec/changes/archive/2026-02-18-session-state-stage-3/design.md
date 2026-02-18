## Context

Stage 1 introduced `SessionState`, Stage 2 introduced the action system (Store, actions, reducers). Stage 3 connects these together:
- Refactor traits to dispatch actions instead of direct mutation
- Integrate Store with StoryContext
- Connect engine to state persistence
- Create action-to-tool mapping

This enables full state management through actions, with state persisted after each agent step.

## Goals / Non-Goals

**Goals:**
- Refactor GraphTrait.transition() to dispatch GraphTransitionAction
- Read current position from session state (not entity fields directly)
- StoryContext owns Store instance
- Tool functions dispatch actions through Store
- Effective field values: combine project defaults + session state overrides
- After agent step: serialize and store state with response message
- Load latest state when reconstructing session
- Action-to-tool mapping for tool calls

**Non-Goals:**
- Trigger evaluation (Stage 4)
- Dynamic field evaluation (`=expression`)
- History/undo (Stage 5)
- Auto-save functionality beyond basic persistence

## Decisions

### 1. GraphTrait reads from state, not entity

**Decision:** GraphTrait methods read current node from session state, not from entity field directly.

**Rationale:**
- Session state is the source of truth for current values
- Enables undo/redo by replaying actions
- Decouples entity definition from runtime state

**Alternatives considered:**
- Read from entity, write to state: Would require sync logic, more complex

### 2. Tool results wrap action results

**Decision:** Tools return `{"result": "success"}` or `{"result": "error", "reason": str}` to indicate action execution status.

**Rationale:**
- Simple contract between tool and LLM
- Error messages are descriptive
- Matches existing tool return format in codebase

### 3. State persisted per response message

**Decision:** After each agent response, serialize session state and store on the response message.

**Rationale:**
- Follows architecture: state stored with model responses
- Enables history traversal later
- Latest state = latest response with non-null state

**Alternatives considered:**
- Store on Session model: Doesn't support history, no per-step snapshots

### 4. StoryContext wraps Store

**Decision:** StoryContext owns Store instance, tool functions access Store via StoryContext.

**Rationale:**
- StoryContext already passed to tools as context (RunContext)
- Tools call `story_context.store.dispatch(action)`
- Effective fields computed from project + session state

**Alternatives considered:**
- Store as separate dependency: Would require changing tool context

### 5. Action-to-tool mapping via trait functions

**Decision:** Traits define tools that dispatch actions. The tool function extracts args from LLM call, dispatches action, returns result.

**Rationale:**
- Follows existing trait pattern (GraphTrait already has transition tool)
- Each trait knows its own actions
- Easy to test: tool function = action dispatch + result wrapping

## Risks / Trade-offs

| Risk | Mitigation |
|------|------------|
| Breaking existing tools | Keep same tool signatures; refactor internally |
| State sync issues | Always read from state, not entity fields |
| Large state blob | Only store deltas (overrides), not full entity |
| Missing state on load | Handle None gracefully; start fresh |

## Migration Plan

1. **Add Store to StoryContext**: Update StoryContext.__init__ to create Store
2. **Refactor GraphTrait**: transition() dispatches action, reads from state
3. **Add effective field methods**: get_effective_field() combines state + project
4. **Update tool context**: Tools access store via StoryContext
5. **Update SessionAdapter.append_messages**: Pass state when saving responses
6. **Update session loading**: Load latest state from message history
7. **Tests**: Full flow tests for action dispatch + persistence

## Open Questions

- Should we store state on every message or only when state changed?
  - Current: always store (simpler, enables history)
- How to handle tool calls that don't change state?
  - Still dispatch action (for logging/triggers), state unchanged
- Should action results be persisted separately?
  - Not in Stage 3; can add later if needed
