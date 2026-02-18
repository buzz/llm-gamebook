## Context

Stage 1 introduced `SessionState` for persisting entity field overrides. Stage 2 builds on that to implement a Redux-inspired action system where all state changes flow through actions. This enables:
- Centralized state change tracking (for debugging, logging)
- Middleware hooks (trigger evaluation, auto-save)
- Reducer composition (multiple handlers can react to same action)
- Future undo/redo by replaying action history

## Goals / Non-Goals

**Goals:**
- Define `Action` base class with `name` (namespaced string) and typed `payload` (Pydantic model)
- Create concrete action classes for game operations (e.g., `GraphTransitionAction`, `EndGameAction`)
- Create `Store` class with `dispatch(action)` method
- Implement middleware chain: Logger, MessageBusPublisher (stub), TriggerEval (stub), AutoSave (stub)
- Define reducer signature: `(State, Action) → State`
- Create reducer registry for trait-based reducer registration
- Implement reducer composition (multiple reducers handle same action)
- Maintain immutability: `dispatch` returns new state object

**Non-Goals:**
- Action-driven state changes (Stage 3) - still using direct mutation in traits
- Trigger evaluation (Stage 4) - middleware is a stub
- Auto-save functionality - middleware is a stub
- Action history/replay (Stage 5)
- MessageBusPublisher implementation (Stage 6) - middleware is a stub

## Decisions

### 1. Action Type: Generic Pydantic Model with typed payload

**Decision:** Actions are generic Pydantic models with a `name` field and typed `payload: T` where `T` extends `BaseModel`.

**Rationale:**
- Type-safe: Payload fields are typed and validated by Pydantic
- Serializable: Pydantic models serialize to JSON easily
- Extensible: New actions just add new payload classes
- Schema validation: Each payload has its own Pydantic schema

**Implementation:**
```python
class Action[T: BaseModel](BaseModel):
    name: str
    payload: T

class GraphTransitionPayload(BaseModel):
    entity_id: str
    to: str

class GraphTransitionAction(Action[GraphTransitionPayload]):
    ...
```

**Alternatives considered:**
- `payload: JsonValue`: No type safety, no schema validation
- Simple dict: `{"name": "graph/transition", "payload": {...}}`: No type safety, harder to validate
- Dataclass: Less serialization support than Pydantic

### 2. Action Names: Namespaced strings

**Decision:** Action types use `namespace/action` format (e.g., `graph/transition`, `core/end-game`).

**Rationale:**
- Prevents collisions between modules
- Clear ownership: `graph/*` from graph trait, `core/*` from core system
- Matches architecture specification

### 3. Store holds SessionState directly

**Decision:** `Store` wraps `SessionState` as its state, not `StoryContext`.

**Rationale:**
- Clear separation: Store handles actions, StoryContext handles project integration
- Simpler: Store only needs to manage session state
- Stage 3 will connect Store to StoryContext

**Alternatives considered:**
- Store wraps StoryContext: Would couple action system too tightly to project

### 4. Reducer Registry: Attached to traits via decorator

**Decision:** Traits register reducers via `@trait_registry.register` decorator with `reducers` method.

**Rationale:**
- Follows existing trait pattern
- Decentralized: Each trait defines its own reducers
- Static registration at import time

**Alternatives considered:**
- Runtime registration: More flexible but more complex
- Central reducer map: Would require importing all traits manually

### 5. Middleware Chain: List of callables

**Decision:** Middleware is a list of functions `(Store, Action) → Action` executed in order.

**Rationale:**
- Simple and explicit
- Easy to add/remove middleware
- Middleware can modify action or dispatch new actions

**Alternatives considered:**
- Class-based middleware: More verbose
- Async middleware: Not needed yet (synchronous Stage 2)

## Risks / Trade-offs

| Risk | Mitigation |
|------|------------|
| Circular middleware dispatch | Limit middleware to 1 additional dispatch, track in progress |
| Performance with many reducers | Composition runs in order, short-circuit if needed |
| Trait not loaded, reducer missing | Log warning if action has no registered reducers |
| State mutation in reducer | Return new state object; validate with Pyright |

## Migration Plan

1. **Create action module**: `backend/llm_gamebook/story/actions.py` with base `Action` class
2. **Create concrete actions**: Add `GraphTransitionAction`, `EndGameAction` to actions.py
3. **Create store module**: `backend/llm_gamebook/story/store.py` with `Store` class
4. **Create reducer infrastructure**: Reducer types, registry in `actions.py` or new module
5. **Create middleware module**: `backend/llm_gamebook/story/middleware.py` with built-in middleware
6. **Update trait registry**: Add reducer registration support
7. **Update graph trait**: Register `graph/transition` reducer
8. **Tests**: Unit tests for dispatch, reducers, middleware

## Open Questions

- Should actions be async?
  - Current design: sync (Stage 2 only)
  - Future: may need async for trigger evaluation
- How to handle reducer errors?
  - Current: raise exception, let caller handle
  - Could wrap in result type
- Built-in actions: what other actions beyond `graph/transition` and `core/end-game`?
  - Defer to Stage 3 when connecting to tools
