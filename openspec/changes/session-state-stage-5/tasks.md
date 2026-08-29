## 1. State Storage Updates

- [x] 1.1 Update to store full state snapshots (not just changes) with each response
- [x] 1.2 Verify state serialization/deserialization handles full state correctly
- [x] 1.3 Add migration if needed for existing sessions

## 2. State Traversal

- [x] 2.1 Implement `find_previous_state(session_id, step_num)` function
- [x] 2.2 Walk messages from oldest to newest
- [x] 2.3 Handle gaps: continue walking when message has null state
- [x] 2.4 Return state from most recent message with state at or before target step
- [x] 2.5 Handle edge case: no previous state exists

## 3. Core Actions

- [x] 3.1 Create `EndGameAction` with payload (optional reason)
- [x] 3.2 Create `ResetGameAction` with no payload
- [x] 3.3 Create `RestoreAction` with payload `{"step": int}` or `{"step": -1}` for latest
- [x] 3.4 Create `ForkAction` with payload `{"step": int}` or `{"step": -1}` for latest
- [x] 3.5 Implement reducers for all core actions

## 4. Restore Functionality

- [x] 4.1 Implement restore reducer: set session state to target state's content
- [x] 4.2 Handle invalid step (greater than current): return error
- [x] 4.3 Update session loading to support restoring to specific point

## 5. Fork Functionality

- [x] 5.1 Implement fork reducer: create new session with state from target
- [x] 5.2 Copy state to new session (not message history)
- [x] 5.3 Return new session ID to caller
- [x] 5.4 Ensure original session is unaffected

## 6. End-Game and Reset

- [x] 6.1 Implement end-game reducer: mark session as ended
- [x] 6.2 Add `ended_at` timestamp to Session model if not present
- [x] 6.3 Implement reset-game reducer: clear all state, reset to defaults
- [x] 6.4 Handle reset: reinitialize session with project defaults

## 7. History Cleanup

- [x] 7.1 Add configuration for max history size (default: 50)
- [x] 7.2 Implement cleanup: remove oldest states beyond limit
- [x] 7.3 Run cleanup on new state storage
- [x] 7.4 Ensure latest states are always preserved

## 8. Testing

- [x] 8.1 Add unit tests for state traversal with gaps
- [x] 8.2 Add unit tests for restore action
- [x] 8.3 Add unit tests for fork action
- [x] 8.4 Add unit tests for end-game action
- [x] 8.5 Add unit tests for reset-game action
- [x] 8.6 Add unit tests for history cleanup
- [x] 8.7 Add integration test for full history flow

## 9. Error Handling

- [x] 9.1 Handle restore to invalid step
- [x] 9.2 Handle fork when no state exists
- [x] 9.3 Handle reset on already-reset session
- [x] 9.4 Log warnings for cleanup failures
