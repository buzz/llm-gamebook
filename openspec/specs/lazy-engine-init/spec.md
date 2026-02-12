## ADDED Requirements

### Requirement: EngineManager defers model/state creation until engine actually needed

The EngineManager SHALL NOT instantiate the Model and StoryState until the first time an engine is requested for a session. When `get_or_create()` is called and no engine exists for the session, the EngineManager SHALL instantiate the Model and StoryState using the provided db_session before creating the StoryEngine.

#### Scenario: First request for session creates engine with lazy initialization

- **WHEN** `EngineManager.get_or_create(session_id, db_session)` is called and no engine exists for `session_id`
- **THEN** EngineManager instantiates Model using db_session
- **AND** EngineManager instantiates StoryState using db_session
- **AND** EngineManager creates StoryEngine with the instantiated model and state
- **AND** EngineManager caches the engine for future requests

#### Scenario: Subsequent requests return cached engine without re-instantiation

- **WHEN** `EngineManager.get_or_create(session_id, db_session)` is called and an engine already exists for `session_id`
- **THEN** EngineManager returns the cached engine
- **AND** EngineManager does NOT re-instantiate Model
- **AND** EngineManager does NOT re-instantiate StoryState
- **AND** EngineManager updates the last-used timestamp

#### Scenario: EngineManager evicts idle engines

- **WHEN** engine has been idle for longer than the configured timeout
- **THEN** EngineManager removes the engine from cache
- **AND** Next request for that session will trigger lazy initialization again
