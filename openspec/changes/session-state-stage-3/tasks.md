## 1. StoryContext Integration with Store

- [ ] 1.1 Update `StoryContext.__init__` to accept optional `SessionState` and create Store instance
- [ ] 1.2 Add `store` property to StoryContext
- [ ] 1.3 Add `get_effective_field(entity_id: str, field_name: str) -> FieldValue | None` method
- [ ] 1.4 Add `set_field(entity_id: str, field_name: str, value: FieldValue) -> None` method
- [ ] 1.5 Implement merge logic: check session state first, fallback to project default

## 2. GraphTrait Refactor

- [ ] 2.1 Refactor `GraphTrait.transition()` to dispatch `GraphTransitionAction` via Store
- [ ] 2.2 Update `current_node` property to read from session state (not cached entity field)
- [ ] 2.3 Update `current_node_id` property to read from session state
- [ ] 2.4 Update `get_template_context()` to use effective field values
- [ ] 2.5 Keep tool function but have it dispatch action and return result
- [ ] 2.6 Remove `StoryContext.set_field()` (state updates only happen through action dispatch)

## 3. Tool Function Updates

- [ ] 3.1 Update tool context: tools receive StoryContext which has store
- [ ] 3.2 Update tool functions to dispatch actions via `story_context.store.dispatch()`
- [ ] 3.3 Update tool return format: `{"result": "success"}` or `{"result": "error", "reason": str}`
- [ ] 3.4 Handle action execution errors and return descriptive messages

## 4. State Persistence

- [ ] 4.1 Update `SessionAdapter.append_messages()` to pass state when saving responses
- [ ] 4.2 Serialize session state to JSON when saving message
- [ ] 4.3 Implement `get_latest_state(session_id)` to find most recent message with state
- [ ] 4.4 Update session loading to restore state from latest response
- [ ] 4.5 Handle case where no state exists (new session)

## 5. Action-to-Tool Mapping

- [ ] 5.1 Define mapping between tool names and action types
- [ ] 5.2 Ensure GraphTrait tools dispatch correct actions with correct payloads
- [ ] 5.3 Handle multiple tool calls in single response (batch dispatch)

## 6. Testing

- [ ] 6.1 Add unit tests for StoryContext effective field values
- [ ] 6.2 Add unit tests for GraphTrait action dispatch
- [ ] 6.3 Add unit tests for tool function action dispatch
- [ ] 6.4 Add integration tests for state persistence through engine flow
- [ ] 6.5 Add tests for session loading with state restoration
- [ ] 6.6 Add tests for multiple tool calls in one response

## 7. Error Handling

- [ ] 7.1 Validate entity exists in project when setting field
- [ ] 7.2 Handle action dispatch errors gracefully
- [ ] 7.3 Handle corrupted state JSON on load gracefully
- [ ] 7.4 Validate transition target exists before dispatching action
