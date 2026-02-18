## 1. Action Classes

- [x] 1.1 Create `backend/llm_gamebook/story/actions.py` with base `Action` Pydantic model (type: str, payload: JsonValue)
- [x] 1.2 Define type alias `ActionType` for namespaced action strings (e.g., `graph/transition`)
- [x] 1.3 Create `GraphTransitionAction` with payload schema `{"to": str}` (in `traits/graph.py`)
- [x] 1.4 Create `EndGameAction` with optional payload
- [x] 1.5 Add action serialization/deserialization tests

## 2. Store Class

- [x] 2.1 Create `backend/llm_gamebook/story/store.py` with `Store` class
- [x] 2.2 Implement `Store.__init__` accepting initial state (SessionState) and optional middleware list
- [x] 2.3 Implement `Store.dispatch(action: Action) -> SessionState` returning new state
- [x] 2.4 Implement `Store.get_state() -> SessionState`
- [x] 2.5 Ensure immutability: dispatch returns new SessionState, original unchanged

## 3. Middleware Infrastructure

- [x] 3.1 Define middleware type: `type Middleware = Callable[[Store, Action], Action]`
- [x] 3.2 Implement middleware chain execution in Store.dispatch
- [x] 3.3 Create `backend/llm_gamebook/story/middleware.py`
- [x] 3.4 Implement Logger middleware (logs action type and payload)
- [x] 3.5 Implement MessageBusPublisher stub middleware (passes action through unchanged, placeholder for Stage 6)
- [x] 3.6 Implement TriggerEval stub middleware (passes action through unchanged)
- [x] 3.7 Implement AutoSave stub middleware (passes action through unchanged)
- [x] 3.8 Add protection against middleware infinite recursion (max 1 additional dispatch)

## 4. Reducer Infrastructure

- [x] 4.1 Define reducer type: `type Reducer = Callable[[SessionState, Action], SessionState]`
- [x] 4.2 Define `type ReducerRegistry = dict[ActionType, list[Reducer]]`
- [x] 4.3 Implement reducer registry in Store
- [x] 4.4 Implement reducer composition: chain registered reducers in order
- [x] 4.5 Handle case when no reducers registered for action type (return unchanged state)

## 5. Trait Reducer Registration

- [x] 5.1 Update `TraitRegistryEntry` to include optional `reducers` mapping
- [x] 5.2 Update `@trait_registry.register` decorator to accept `reducers` parameter
- [x] 5.3 Add method to retrieve all registered reducers from registry
- [x] 5.4 Load trait reducers into Store on initialization

## 6. Graph Trait Reducer

- [x] 6.1 Add `reducers()` method to `GraphTrait` class returning `{"graph/transition": reducer_fn}`
- [x] 6.2 Implement graph transition reducer: extracts `to` from action payload, updates entity's current_node_id
- [x] 6.3 Register graph trait reducers via decorator parameter

## 7. Testing

- [x] 7.1 Add unit tests for Action classes (serialization, type field)
- [x] 7.2 Add unit tests for Store.dispatch (immutability, returns new state)
- [x] 7.3 Add unit tests for middleware chain (order, modification)
- [x] 7.4 Add unit tests for reducer composition (multiple reducers)
- [x] 7.5 Add unit tests for trait reducer registration
- [x] 7.6 Add integration test for full dispatch flow: action → middleware → reducer → new state

## 8. Error Handling

- [x] 8.1 Add validation for action type format (must be `namespace/action`)
- [x] 8.2 Handle invalid action types gracefully with descriptive error
- [x] 8.3 Validate reducer return value is new SessionState instance
