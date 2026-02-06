## Why

Currently, `get_model_state()` is called on every request to create the Model and StoryState, even when an EngineManager already has a cached engine for that session. This wastes CPU cycles on:
- Project YAML parsing and validation (expensive - reads from disk, parses, validates)
- LLM model configuration and HTTP client creation

The engine should only be created when it doesn't exist, and model/state creation should happen inside the EngineManager on demand, not before checking the cache.

## What Changes

- **Remove** `get_model_state()` function (temporary placeholder no longer needed)
- **Modify** `EngineManager.get_or_create()` to accept `db_session` parameter and instantiate model/state lazily
- **Add** `StoryEngine.set_model()` method to update engine's model at runtime without recreation
- **Add** model config change notification via event bus (when session's model config changes, notify engine manager)
- **Modify** FastAPI deps to pass only `session_id` and `db_session` to engine manager

**BREAKING:** `get_model_state()` function removed. EngineManager now handles instantiation directly.

## Capabilities

### New Capabilities
- `engine-manager-lazy-init`: EngineManager defers model/state creation until engine actually needed (on first access for a session)
- `engine-model-update`: StoryEngine can update its model at runtime without recreation
- `model-config-change-notification`: Event system for notifying engine manager of config changes per session

### Modified Capabilities
None (existing functionality preserved, just deferred)

## Impact

**Files to modify:**
- `backend/llm_gamebook/web/get_model.py` - Remove file
- `backend/llm_gamebook/engine/manager.py` - Add lazy instantiation in get_or_create(), accept db_session
- `backend/llm_gamebook/engine/engine.py` - Add set_model() method
- `backend/llm_gamebook/web/api/deps.py` - Pass session_id and db_session only
- `backend/llm_gamebook/web/websocket/handler.py` - Pass session_id and db_session only
- `backend/llm_gamebook/web/app.py` - Add model config change listener
- `backend/llm_gamebook/db/models/session.py` - Add relationship for ModelConfig changes
- `backend/llm_gamebook/message_bus.py` - Add new event type for config changes

**Dependencies:**
- No new dependencies required
- Uses existing message bus for notifications
- EngineManager now depends on db_session for lazy instantiation
