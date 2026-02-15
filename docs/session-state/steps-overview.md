# Session State Implementation Stages

## Current State

The codebase has:
- **Project loading**: YAML → `Project` / `EntityType` objects with trait mixins
- **Condition system**: Boolean expression grammar with dot-path resolution
- **Graph trait**: Nodes with transitions (modifies entity state directly)
- **Message bus**: Publish/subscribe event system
- **Session storage**: Database models for conversation history

Not implemented (from architecture.md):
- Session state persistence layer (separate from project)
- Action system (actions, reducers, middleware)
- Dynamic field evaluation (`=expression`)
- Trigger system
- State history/undo

## Stage 1: Core State Infrastructure

### Overview
Add database schema support for session state and create the core state management classes.

### Units of Work

1. **Add state field to database models**
   - Add `state: dict | None` field to `Message` model
   - Create migration if needed

2. **Create SessionState class**
   - Holds entity field overrides (dict structure)
   - Provides get/set methods for entity fields
   - Handles merging with project defaults

3. **Implement state serialization**
   - Serialize state to JSON for storage
   - Deserialize from JSON on load

4. **Integrate with StoryContext**
   - Update `StoryContext` to hold both project + session state
   - Add method to get effective field values (state overrides + defaults)

### Test Cases
- Load project with default values, verify effective values match
- Set override in session state, verify effective values reflect override
- Serialize/deserialize state roundtrip preserves data
- Loading existing session merges stored state with current project defaults
- Project field removal: state contains orphaned fields that should be dropped
- Project field addition: missing fields get defaults from project

---

## Stage 2: Action System

### Overview
Implement the Redux-inspired action system with dispatch, reducers, and middleware.

### Units of Work

1. **Define action classes**
   - Create base `Action` class with type, payload
   - Create concrete actions: `GraphTransitionAction`, `EndGameAction`, etc.
   - Use namespaced action names: `namespace/action`

2. **Create Store class**
   - Holds current state
   - Provides `dispatch(action)` method
   - Applies middleware chain before reducers

3. **Implement reducer infrastructure**
   - Define reducer function signature: `(State, Action) → State`
   - Create reducer registry (traits can register reducers)
   - Implement reducer composition

4. **Define middleware chain**
   - Logger middleware
   - MessageBusPublisher middleware (stub)
   - Trigger evaluation middleware (stub)
   - Auto-save middleware (stub)

### Test Cases
- Dispatch action reaches reducers in correct order
- Multiple reducers can handle same action (composition)
- Middleware can modify action before passing to reducers
- Middleware can dispatch additional actions
- Store returns new state object on each dispatch (immutability)
- Invalid action type raises appropriate error

---

## Stage 3: Action-Driven State Changes

### Overview
Replace direct entity mutations with action dispatch, integrate with the engine.

### Units of Work

1. **Refactor graph trait to dispatch actions**
   - `GraphTrait.transition()` dispatches `GraphTransitionAction` instead of direct mutation
   - Read current position from state, not entity

2. **Integrate store with StoryContext**
   - StoryContext owns the Store
   - Tool functions dispatch actions through store
   - Effective field values combine project defaults + state overrides

3. **Connect engine to state persistence**
   - After agent step completes, serialize and store state with response message
   - Load latest state when reconstructing session

4. **Create action-to-tool mapping**
   - Define how tool calls map to action dispatch
   - Handle action results (success/error)

### Test Cases
- Tool call dispatches correct action
- State changes persist after agent response
- Loading session restores state correctly
- Tool result reflects action execution (success/error)
- Multiple tool calls in one response all persist state

---

## Stage 4: Trigger System

### Overview
Implement condition-based action dispatch after agent steps.

### Units of Work

1. **Parse trigger definitions**
   - Add trigger support to entity type definitions in schema
   - Load triggers when building entity types

2. **Create trigger evaluation middleware**
   - Evaluate all triggers after each agent step
   - Dispatch trigger actions when conditions are true

3. **Implement trigger condition evaluation**
   - Integrate BoolExprEvaluator with current state
   - Handle dynamic field references in conditions

### Test Cases
- Trigger fires when condition evaluates to true
- Trigger does not fire when condition is false
- Multiple triggers can fire in same step
- Trigger dispatch happens after state changes are committed
- Invalid condition expression raises error

---

## Stage 5: History and Undo

### Overview
Enable going back to previous states, supporting save games and branching.

### Units of Work

1. **Store state with each agent response**
   - Serialize complete state after each step
   - Attach to response message in database

2. **Implement state traversal**
   - Walk back through message history to find previous states
   - Handle gaps (responses without state changes)

3. **Add restore functionality**
   - Create action to restore to specific point
   - Fork support: branch from any historical state

4. **Implement core/end-game/reset actions**
   - `core/end-game`: Mark session as ended
   - `core/reset-game`: Clear state and restart

### Test Cases
- State after step N matches serialized state in message N
- Can traverse back to any previous state
- Restore to previous state makes it current
- Fork creates independent branch
- Reset clears all state and restarts from defaults
- State history doesn't grow unbounded (cleanup old snapshots)

---

## Stage 6: Message Bus Bridge

### Overview
Implement the MessageBusPublisher middleware to bridge the action system to the application's message bus. This enables external plugins and application components to observe story actions without coupling to the action system.

### Units of Work

1. **Define ActionDispatched message**
   - Create `ActionDispatched` message class in message module
   - Include: `session_id`, `action_type`, `payload`, `timestamp`

2. **Create MessageBusPublisher middleware**
   - Accept `MessageBus` instance and optional action filter pattern
   - Publish `ActionDispatched` message after action is dispatched (before reducers)
   - Support filtering: all actions, or only specific namespaces (e.g., `core/*`)

3. **Integrate with Store**
   - Add MessageBusPublisher to middleware chain (position after Logger, before Triggers)
   - Pass MessageBus instance to store at creation time

4. **Support plugin development**
   - Document how to subscribe to ActionDispatched messages
   - Example: UI plugin listens for `core/end-game` to show ending

### Test Cases
- ActionDispatched message is published when action is dispatched
- Message contains correct session_id, action_type, payload
- Filter pattern correctly includes/excludes actions
- Multiple subscribers can handle same message
- Middleware doesn't block if message bus is not available

### Dependencies
- Stage 2 (action system with middleware chain)
- Message bus already exists in codebase

---

## Dependencies Between Stages

```
Stage 1: Core State Infrastructure
    │
    ├─ Stage 2: Action System
    │       │
    │       └─ Stage 3: Action-Driven State Changes
    │               │
    │               ├─ Stage 4: Trigger System
    │               │
    │               └─ Stage 5: History and Undo
    │
    └─ Stage 6: Message Bus Bridge
```

- Stage 1 is foundational (all subsequent stages depend on it)
- Stage 2 builds on Stage 1's state infrastructure
- Stage 3 connects actions to the engine (requires both Stage 1 and 2)
- Stage 4 and 5 can be developed somewhat independently after Stage 3
- Stage 4 (triggers) and 5 (history) could run in parallel after Stage 3
- Stage 6 depends on Stage 2 (middleware chain) but is otherwise independent

## Non-Disruptive Considerations

1. **Stage 1** is purely additive (new database column, new classes)
2. **Stage 2** adds new action infrastructure without changing existing behavior
3. **Stage 3** requires refactoring existing traits - should add compatibility layer initially
4. **Stage 4** can be developed with trigger evaluation disabled by default
5. **Stage 5** should preserve existing message format, just add new optional fields
6. **Stage 6** is additive middleware - doesn't change action behavior, only publishes events
