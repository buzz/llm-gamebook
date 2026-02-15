## ADDED Requirements

### Requirement: Message model stores session state
The system SHALL store session state as a JSON blob on the `Message` model to enable persistence with model responses.

#### Scenario: Response message with state
- **GIVEN** a user is playing a game session
- **WHEN** the model responds with a message after an agent step
- **THEN** the message SHALL contain a `state` field with the current entity field overrides serialized as JSON

#### Scenario: Request message without state
- **GIVEN** a user is playing a game session
- **WHEN** a request message is created
- **THEN** the message SHALL have `state` set to `null`

#### Scenario: Null state for unchanged responses
- **GIVEN** a model response that does not modify any entity fields
- **WHEN** the message is saved
- **THEN** the `state` field MAY be `null`

### Requirement: SessionState class manages entity field overrides
The system SHALL provide a `SessionState` class that holds entity field overrides separately from the project definition.

#### Scenario: Create empty session state
- **GIVEN** a new game session
- **WHEN** `SessionState` is instantiated
- **THEN** the internal overrides dict SHALL be empty

#### Scenario: Set entity field override
- **GIVEN** a `SessionState` instance with an existing project
- **WHEN** `set_field(entity_id, field_name, value)` is called
- **THEN** the value SHALL be stored in the overrides dict under the entity's key

#### Scenario: Get entity field override
- **GIVEN** a `SessionState` instance with a previously set override
- **WHEN** `get_field(entity_id, field_name)` is called for an overridden field
- **THEN** the override value SHALL be returned

#### Scenario: Get field returns None for unset
- **GIVEN** a `SessionState` instance with no overrides for a field
- **WHEN** `get_field(entity_id, field_name)` is called
- **THEN** `None` SHALL be returned

### Requirement: SessionState provides JSON serialization
The system SHALL support serializing `SessionState` to JSON for persistence and deserializing from JSON.

#### Scenario: Serialize session state to JSON
- **GIVEN** a `SessionState` with multiple entity field overrides
- **WHEN** `to_json()` is called
- **THEN** a valid JSON string SHALL be returned representing the overrides dict

#### Scenario: Deserialize session state from JSON
- **GIVEN** a valid JSON string representing session state
- **WHEN** `SessionState.from_json(json_string)` is called
- **THEN** a `SessionState` instance SHALL be returned with the overrides populated

#### Scenario: Roundtrip preserves data
- **GIVEN** a `SessionState` with entity field overrides
- **WHEN** the state is serialized to JSON and then deserialized
- **THEN** the resulting `SessionState` SHALL contain the same overrides

### Requirement: StoryState integrates session and project state
The system SHALL update `StoryState` to hold both project and session state, providing access to effective field values.

#### Scenario: Effective field returns project default
- **GIVEN** a `StoryState` with a project containing an entity with field `x = "default"`
- **AND** no session state override for field `x`
- **WHEN** `get_effective_field(entity_id, field_name)` is called
- **THEN** the project default value SHALL be returned

#### Scenario: Effective field returns session override
- **GIVEN** a `StoryState` with a project containing an entity with field `x = "default"`
- **AND** session state override sets `x = "override"`
- **WHEN** `get_effective_field(entity_id, field_name)` is called
- **THEN** the override value `"override"` SHALL be returned

#### Scenario: Set field through StoryState
- **GIVEN** a `StoryState` instance
- **WHEN** `set_field(entity_id, field_name, value)` is called
- **THEN** the value SHALL be stored in session state

### Requirement: State merge handles project changes
The system SHALL handle gracefully cases where the project definition changes between sessions.

#### Scenario: Orphaned fields in state are dropped
- **GIVEN** a session state with override for field `x` that no longer exists in the project
- **WHEN** effective field is accessed
- **THEN** the orphaned field SHALL be ignored and project default (if any) used

#### Scenario: Missing fields get project defaults
- **GIVEN** a project that defines a new field `y` not in the stored session state
- **WHEN** effective field is accessed for field `y`
- **THEN** the project default value SHALL be returned

### Requirement: Load session restores latest state
The system SHALL load the most recent state when reconstructing a session from the database.

#### Scenario: Load session with existing messages
- **GIVEN** a session with multiple message responses, some with state
- **WHEN** the session is loaded
- **THEN** the session state SHALL be restored from the most recent message with non-null state

#### Scenario: Load new session has empty state
- **GIVEN** a new session with no previous messages
- **WHEN** the session is loaded
- **THEN** the session state SHALL be empty
