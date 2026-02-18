## Why

With Stage 1's session state infrastructure in place, the codebase still mutates entity fields directly. Stage 2 implements a Redux-inspired action system where all state changes go through actions, enabling the trigger system, middleware hooks, and future undo/redo functionality.

## What Changes

- Define base `Action` class with `type` (namespaced string) and `payload` (`JsonValue`)
- Create concrete action classes: `GraphTransitionAction`, `EndGameAction`, etc.
- Use namespaced action names (`namespace/action` format)
- Create `Store` class holding current state with `dispatch(action)` method
- Apply middleware chain before reducers on each dispatch
- Define reducer function signature: `(State, Action) → State`
- Create reducer registry where traits can register reducers
- Implement reducer composition (multiple reducers can handle same action)
- Define middleware chain: Logger, TriggerEval (stub), AutoSave (stub)
- Store returns new state object on each dispatch (immutability)

## Capabilities

### New Capabilities

- `action-system`: Redux-inspired action system with dispatch, reducers, and middleware chain

### Modified Capabilities

- (none)

## Impact

- **Backend**: New `Action` classes, `Store` class, reducer registry in `story/` module
- **Traits**: Update trait registry to support reducer registration
- **Testing**: New tests for dispatch flow, reducer composition, middleware
