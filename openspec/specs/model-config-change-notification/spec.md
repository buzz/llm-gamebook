## ADDED Requirements

### Requirement: Event system notifies engine manager of model config changes per session

When a session's model configuration is updated in the database, the system SHALL publish an event to the message bus that the EngineManager can subscribe to. Upon receiving this event, if an engine is currently active for that session, the EngineManager SHALL update the engine's model using the new configuration.

#### Scenario: Model config updated for session with active engine

- **WHEN** session's `model_config_id` is updated in database
- **AND** EngineManager has an active engine for that session
- **THEN** system publishes `session.model_config.changed` event with session_id and new config_id
- **AND** EngineManager receives the event
- **THEN** EngineManager creates new Model using new config from database
- **AND** EngineManager calls `StoryEngine.set_model(new_model)` to update the engine

#### Scenario: Model config updated for session without active engine

- **WHEN** session's `model_config_id` is updated in database
- **AND** EngineManager does NOT have an active engine for that session
- **THEN** system publishes `session.model_config.changed` event
- **AND** EngineManager ignores the event (no engine to update)
- **AND** Next request for session will use new config during lazy initialization

#### Scenario: Multiple model config updates in succession

- **WHEN** session's `model_config_id` is updated multiple times rapidly
- **THEN** each update publishes a separate `session.model_config.changed` event
- **AND** EngineManager processes each event in order
- **AND** Engine uses the most recent config after all updates processed
