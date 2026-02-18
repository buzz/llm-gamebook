## ADDED Requirements

### Requirement: StoryContext owns Store instance
The system SHALL have StoryContext own a Store instance that manages session state through actions.

#### Scenario: StoryContext initializes with Store
- **GIVEN** a StoryContext is created
- **WHEN** initialized
- **THEN** it SHALL create a Store instance with the session state

#### Scenario: Tools access store via StoryContext
- **GIVEN** a tool function receives StoryContext as context
- **WHEN** the tool needs to change state
- **THEN** it SHALL access the store via `story_context.store.dispatch(action)`

### Requirement: GraphTrait dispatches actions instead of direct mutation
The system SHALL refactor GraphTrait to dispatch GraphTransitionAction rather than mutating entity fields directly.

#### Scenario: Transition dispatches action
- **GIVEN** a GraphTrait with current_node set
- **WHEN** transition(to) is called
- **THEN** it SHALL dispatch a GraphTransitionAction with payload `{"to": to, "entity_id": entity.id}`
- **AND** it SHALL NOT mutate _current_node directly

#### Scenario: Current node read from state
- **GIVEN** a GraphTrait with session state containing current_node_id override
- **WHEN** accessing current_node property
- **THEN** it SHALL read from session state, not from cached entity field
- **AND** resolve the node ID to the actual node entity

### Requirement: Effective field values combine project defaults and session state
The system SHALL provide a method to get effective field values that merge project defaults with session state overrides.

#### Scenario: Effective field returns state override
- **GIVEN** session state has override for entity.field = "override_value"
- **AND** project has default for entity.field = "default_value"
- **WHEN** get_effective_field(entity_id, "field") is called
- **THEN** it SHALL return "override_value"

#### Scenario: Effective field returns project default
- **GIVEN** session state has no override for entity.field
- **AND** project has default for entity.field = "default_value"
- **WHEN** get_effective_field(entity_id, "field") is called
- **THEN** it SHALL return "default_value"

#### Scenario: Effective field returns None if not in project
- **GIVEN** session state has override for entity.field that no longer exists in project
- **WHEN** get_effective_field(entity_id, "field") is called
- **THEN** it SHALL return None (field no longer exists)

### Requirement: Tool functions dispatch actions through Store
The system SHALL have tool functions dispatch actions through the Store and return results.

#### Scenario: Tool dispatches action successfully
- **GIVEN** a tool function that needs to change state
- **WHEN** called with valid arguments
- **THEN** it SHALL dispatch an action through the store
- **AND** return `{"result": "success"}`

#### Scenario: Tool returns error on action failure
- **GIVEN** a tool function that fails to execute action
- **WHEN** called
- **THEN** it SHALL return `{"result": "error", "reason": "<descriptive error>"}`

### Requirement: State persisted with response messages
The system SHALL serialize and store session state with each response message.

#### Scenario: State saved after agent response
- **GIVEN** an agent step that resulted in state changes
- **WHEN** the response is saved
- **THEN** the session state SHALL be serialized and stored in the message's state field

#### Scenario: State not saved when unchanged
- **GIVEN** an agent step with no state changes
- **WHEN** the response is saved
- **THEN** the message's state field MAY be null (no change to persist)

### Requirement: Session loading restores latest state
The system SHALL load the most recent state when reconstructing a session.

#### Scenario: Load session with state history
- **GIVEN** a session with multiple messages, some with state
- **WHEN** the session is loaded
- **THEN** the Store SHALL be initialized with the state from the most recent message with non-null state

#### Scenario: Load new session has empty state
- **GIVEN** a new session with no messages or no messages with state
- **WHEN** the session is loaded
- **THEN** the Store SHALL be initialized with empty state

### Requirement: Action-to-tool mapping
The system SHALL define how tool calls from the LLM map to action dispatch.

#### Scenario: Tool call dispatches correct action
- **GIVEN** an LLM makes a tool call
- **WHEN** the tool function executes
- **THEN** it SHALL dispatch the correct action type with correct payload

#### Scenario: Multiple tool calls in one response
- **GIVEN** an LLM makes multiple tool calls in one response
- **WHEN** each tool executes
- **THEN** each SHALL dispatch its own action
- **AND** all state changes SHALL be accumulated in the final state
