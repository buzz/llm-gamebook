## Context

### Current State

The FastAPI application uses an `EngineManager` to cache `StoryEngine` instances per session. When a request comes in:

1. FastAPI deps call `get_model_state(db_session, session_id)` which:
   - Loads Project YAML from disk (expensive: read + parse + validate)
   - Creates StoryState with the Project
   - Queries database for session's model config
   - Creates Model instance with HTTP client and provider configuration

2. `EngineManager.get_or_create(session_id, model, state)` checks if engine exists:
   - If exists: returns cached engine (model/state were wasted)
   - If not: creates new engine with passed model/state

**Problem:** Model and StoryState are created on every request, even when engine is cached.

### Constraints

- EngineManager is created at FastAPI startup and lives for app lifetime
- Message bus is used for event publishing/subscribing
- FastAPI uses dependency injection for db_session and engine_mgr
- WebSocket and REST endpoints both use same engine manager
- Session's model config can change during runtime (user switches models)

## Goals / Non-Goals

**Goals:**
- Defer model/state instantiation until engine actually needed (lazy initialization)
- Allow engine to update its model at runtime without recreation
- Notify engine manager when session's model config changes
- Maintain backward compatibility with existing API where possible

**Non-Goals:**
- Changing engine eviction logic (idle timeout remains same)
- Adding new caching strategies beyond what's described
- Changing how sessions or model configs are stored
- Adding distributed caching or multi-server support

## Decisions

### Decision 1: EngineManager handles lazy instantiation

**Approach:** EngineManager's `get_or_create()` accepts `db_session` and instantiates model/state internally.

**Rationale:**
- Keeps instantiation logic close to caching logic
- EngineManager already depends on db_session for engine lifecycle
- Avoids passing factory lambdas through dependency chain
- Simplest change to current architecture

**Alternatives considered:**
- Factory pattern in deps layer → More complex, factory called every request
- Separate state/model cache layer → Overkill, adds complexity
- Hybrid approach → Too complex for current needs

### Decision 2: StoryEngine.set_model() for runtime updates

**Approach:** Add `StoryEngine.set_model(new_model)` method to replace model at runtime.

**Rationale:**
- Allows model config changes without losing engine state
- Preserves session history and agent configuration
- Minimal code changes to engine class

**Implementation details:**
- Replace `self._agent` with new Agent created from new model
- Keep same StoryState, tools, and callbacks
- Ensure thread-safe replacement (atomic assignment)

**Alternatives considered:**
- Destroy and recreate engine on config change → Lose state, more disruptive
- Agent.update_model() → Not supported by Pydantic AI

### Decision 3: Event bus for config change notifications

**Approach:** When session's `model_config_id` changes, publish `session.model_config.changed` event. EngineManager subscribes and updates engine if active.

**Rationale:**
- Decouples config update logic from engine management
- Uses existing message bus infrastructure
- Clean separation of concerns

**Implementation details:**
- Add event type: `session.model_config.changed` with payload `{session_id: UUID, new_config_id: UUID}`
- EngineManager subscribes in constructor
- Handler checks if engine exists, calls `set_model()` if so

**Alternatives considered:**
- Polling for config changes → Inefficient, delayed updates
- Direct callback from session update → Tightly couples layers
- Event only for active engines → Misses future requests

### Decision 4: Remove get_model_state() function

**Approach:** Remove the temporary `get_model_state()` function entirely.

**Rationale:**
- Was a placeholder for development
- No longer needed with lazy initialization
- Logic moves into EngineManager

**Migration:**
- EngineManager now contains the instantiation logic
- FastAPI deps pass only `session_id` and `db_session`

## Risks / Trade-offs

**[Race condition on model config change]** → Mitigation: Event bus processes events sequentially, engine uses most recent config after all updates. For concurrent requests, use atomic model replacement.

**[Memory leak if engine never evicted]** → Mitigation: Existing idle timeout eviction still applies. EngineManager tracks last-used timestamp.

**[Config change during active request]** → Mitigation: `set_model()` is atomic assignment. In-progress request uses old model, subsequent requests use new model. Acceptable trade-off for simplicity.

**[DB session lifetime]** → Mitigation: EngineManager doesn't hold db_session. Each `get_or_create()` call gets fresh session from FastAPI dependency chain.

## Migration Plan

1. **Phase 1: Add set_model() to StoryEngine**
   - Add method to replace internal Agent
   - Test with unit tests

2. **Phase 2: Modify EngineManager.get_or_create()**
   - Accept db_session parameter
   - Add lazy instantiation logic
   - Test with integration tests

3. **Phase 3: Add model config change listener**
   - Publish event when session model changes
   - EngineManager subscribes and updates engine
   - Test with integration tests

4. **Phase 4: Update FastAPI deps**
   - Remove get_model_state() call
   - Pass only session_id and db_session
   - Test all endpoints

5. **Phase 5: Remove get_model_state() file**
   - Delete file after confirming no references
   - Clean up imports
