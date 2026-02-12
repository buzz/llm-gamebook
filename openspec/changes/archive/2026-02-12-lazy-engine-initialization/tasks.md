## 1. Add set_model() to StoryEngine

- [x] 1.1 Add `set_model(new_model)` method to StoryEngine class
- [x] 1.2 Method creates new Agent with new model, preserves StoryState, tools, and callbacks
- [x] 1.3 Ensure atomic replacement of internal _agent attribute (thread-safe)
- [x] 1.4 Add unit tests for set_model() functionality

## 2. Modify EngineManager for lazy instantiation

- [x] 2.1 Update `get_or_create()` signature to accept `db_session` parameter
- [x] 2.2 Add model instantiation logic using db_session and session_id
- [x] 2.3 Add StoryState instantiation logic using db_session and session_id
- [x] 2.4 Keep existing caching logic (check if engine exists, bump timestamp)
- [x] 2.5 Add unit tests for lazy initialization behavior

## 3. Add model config change notification

- [x] 3.1 Add new event type `session.model_config.changed` to message bus
- [x] 3.2 Event payload includes session_id and new_config_id
- [x] 3.3 EngineManager subscribes to `session.model_config.changed` event in constructor
- [x] 3.4 Event handler checks if engine exists for session
- [x] 3.5 If engine exists, creates new Model and calls set_model()
- [x] 3.6 If engine doesn't exist, ignores event (lazy init will use new config)

## 4. Update FastAPI deps to use lazy initialization

- [x] 4.1 Remove get_model_state() function and file
- [ ] 4.2 Update `_get_engine_rest()` to pass only session_id and db_session
- [ ] 4.3 Update `_get_engine_ws()` to pass only session_id and db_session
- [ ] 4.4 Update websocket handler to use new dependency pattern
- [ ] 4.5 Test REST endpoints still work correctly
- [ ] 4.6 Test WebSocket endpoints still work correctly

## 5. Update session model config change handling

- [x] 5.1 Add event publishing when session's model_config_id is updated
- [x] 5.2 Add database trigger or CRUD wrapper to publish event
- [ ] 5.3 Test event is published when model config changes
- [ ] 5.4 Test engine updates when config changes (if active)
- [ ] 5.5 Test lazy initialization uses new config (if no active engine)

## 6. Cleanup and verification

- [x] 6.1 Remove get_model_state() file after confirming no references
- [x] 6.2 Clean up imports across codebase
- [x] 6.3 Run type checking (mypy)
- [x] 6.4 Run linting (ruff)
- [ ] 6.5 Run all tests
- [ ] 6.6 Verify no regressions in existing functionality
