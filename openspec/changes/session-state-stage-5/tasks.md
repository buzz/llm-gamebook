## 1. State Storage Updates

- [ ] 1.1 Update to store full state snapshots (not just changes) with each response
- [ ] 1.2 Verify state serialization/deserialization handles full state correctly
- [ ] 1.3 Add migration if needed for existing sessions

## 2. State Traversal

- [ ] 2.1 Implement `find_previous_state(session_id, step_num)` function
- [ ] 2.2 Walk messages from oldest to newest
- [ ] 2.3 Handle gaps: continue walking when message has null state
- [ ] 2.4 Return state from most recent message with state at or before target step
- [ ] 2.5 Handle edge case: no previous state exists

## 3. Core Actions

- [ ] 3.1 Create `EndGameAction` with payload (optional reason)
- [ ] 3.2 Create `ResetGameAction` with no payload
- [ ] 3.3 Create `RestoreAction` with payload `{"step": int}` or `{"step": -1}` for latest
- [ ] 3.4 Create `ForkAction` with payload `{"step": int}` or `{"step": -1}` for latest
- [ ] 3.5 Implement reducers for all core actions

## 4. Restore Functionality

- [ ] 4.1 Implement restore reducer: set session state to target state's content
- [ ] 4.2 Handle invalid step (greater than current): return error
- [ ] 4.3 Update session loading to support restoring to specific point

## 5. Fork Functionality

- [ ] 5.1 Implement fork reducer: create new session with state from target
- [ ] 5.2 Copy state to new session (not message history)
- [ ] 5.3 Return new session ID to caller
- [ ] 5.4 Ensure original session is unaffected

## 6. End-Game and Reset

- [ ] 6.1 Implement end-game reducer: mark session as ended
- [ ] 6.2 Add `ended_at` timestamp to Session model if not present
- [ ] 6.3 Implement reset-game reducer: clear all state, reset to defaults
- [ ] 6.4 Handle reset: reinitialize session with project defaults

## 7. History Cleanup

- [ ] 7.1 Add configuration for max history size (default: 50)
- [ ] 7.2 Implement cleanup: remove oldest states beyond limit
- [ ] 7.3 Run cleanup on new state storage
- [ ] 7.4 Ensure latest states are always preserved

## 8. Testing

- [ ] 8.1 Add unit tests for state traversal with gaps
- [ ] 8.2 Add unit tests for restore action
- [ ] 8.3 Add unit tests for fork action
- [ ] 8.4 Add unit tests for end-game action
- [ ] 8.5 Add unit tests for reset-game action
- [ ] 8.6 Add unit tests for history cleanup
- [ ] 8.7 Add integration test for full history flow

## 9. Error Handling

- [ ] 9.1 Handle restore to invalid step
- [ ] 9.2 Handle fork when no state exists
- [ ] 9.3 Handle reset on already-reset session
- [ ] 9.4 Log warnings for cleanup failures
