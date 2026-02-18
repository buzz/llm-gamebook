## Why

With Stage 1 (SessionState) and Stage 2 (Action System) implemented, the codebase still mutates entity fields directly in traits. Stage 3 replaces direct mutations with action dispatch, integrates the Store with StoryContext, and connects the engine to state persistence, enabling full state management through actions.

## What Changes

- Refactor `GraphTrait.transition()` to dispatch `GraphTransitionAction` instead of direct mutation
- Read current position from session state, not entity fields
- Integrate Store with StoryContext: StoryContext owns the Store instance
- Tool functions dispatch actions through the Store
- Effective field values combine project defaults + session state overrides
- After agent step completes, serialize and store state with response message
- Load latest state when reconstructing session from database
- Create action-to-tool mapping: define how tool calls map to action dispatch
- Handle action results (success/error) returned to LLM

## Capabilities

### New Capabilities

- `action-driven-state`: Integration of action system with engine for state changes

### Modified Capabilities

- `action-system`: Now connected to StoryContext and engine (was stub middleware)

## Impact

- **Engine**: New state persistence after agent responses
- **StoryContext**: Owns Store, provides effective field values
- **GraphTrait**: Refactored to dispatch actions instead of direct mutation
- **Tool functions**: Now dispatch actions through Store
- **Session loading**: Restores latest state from message history
