## ADDED Requirements

### Requirement: Action base class defines structure
The system SHALL provide a base `Action` class that all actions extend, containing a `type` field with namespaced action name and a `payload`.

#### Scenario: Action has type and payload
- **GIVEN** an action class extending the base `Action`
- **WHEN** the action is instantiated
- **THEN** it SHALL have a `type` attribute with format `namespace/action` (e.g., `graph/transition`)
- **AND** it SHALL have a `payload` attribute as a `JsonValue`

#### Scenario: Action is serializable
- **GIVEN** an instantiated action
- **WHEN** serialized to JSON
- **THEN** the resulting JSON SHALL be deserializable back to an equivalent action

### Requirement: Store provides dispatch method
The system SHALL provide a `Store` class that holds state and provides a `dispatch(action)` method that returns a new state object.

#### Scenario: Dispatch returns new state
- **GIVEN** a `Store` with current state
- **WHEN** `dispatch(action)` is called
- **THEN** a new state object SHALL be returned
- **AND** the original state SHALL remain unchanged (immutability)

#### Scenario: Store holds initial state
- **GIVEN** a `Store` initialized with initial state
- **WHEN** `dispatch` is not called
- **THEN** `get_state()` SHALL return the initial state

### Requirement: Middleware chain processes actions
The system SHALL support a middleware chain that processes each action before reducers.

#### Scenario: Middleware executes in order
- **GIVEN** a Store with middleware [A, B, C]
- **WHEN** an action is dispatched
- **THEN** middleware A SHALL process the action first
- **AND** middleware B SHALL process the result from A
- **AND** middleware C SHALL process the result from B
- **AND** the final action SHALL reach the reducers

#### Scenario: Middleware can modify action
- **GIVEN** a middleware that adds a field to payload
- **WHEN** the action passes through middleware
- **THEN** the modified action SHALL reach the reducers

#### Scenario: Middleware can dispatch additional actions
- **GIVEN** a middleware that dispatches another action
- **THEN** the additional action SHALL also go through the middleware chain
- **AND** this SHALL not cause infinite recursion (max 1 additional dispatch)

### Requirement: Reducers process actions to produce new state
The system SHALL define a reducer signature and support multiple reducers handling the same action.

#### Scenario: Reducer signature
- **GIVEN** a reducer function
- **WHEN** called with (state, action)
- **THEN** it SHALL return a new state object

#### Scenario: Multiple reducers handle same action
- **GIVEN** two reducers registered for action type `graph/transition`
- **WHEN** `graph/transition` action is dispatched
- **THEN** both reducers SHALL be called in registration order
- **AND** each reducer SHALL receive the output of the previous reducer

#### Scenario: No reducer for action
- **GIVEN** an action with no registered reducers
- **WHEN** the action is dispatched
- **THEN** the state SHALL remain unchanged

### Requirement: Traits can register reducers
The system SHALL allow traits to register reducers for actions they handle.

#### Scenario: Trait registers reducer
- **GIVEN** a trait with a `reducers()` method returning a mapping
- **WHEN** the trait is loaded
- **THEN** the reducers SHALL be available in the reducer registry

#### Scenario: Graph trait registers transition reducer
- **GIVEN** the graph trait is loaded
- **WHEN** a `graph/transition` action is dispatched
- **THEN** the graph reducer SHALL handle the action and update current_node

### Requirement: Built-in middleware
The system SHALL provide built-in middleware: Logger, TriggerEval (stub), AutoSave (stub).

#### Scenario: Logger middleware
- **GIVEN** Logger middleware is configured
- **WHEN** an action is dispatched
- **THEN** the action details SHALL be logged

#### Scenario: TriggerEval middleware is stub
- **GIVEN** TriggerEval middleware is configured
- **WHEN** an action is dispatched
- **THEN** it SHALL pass the action through without evaluation (Stage 4 feature)

#### Scenario: AutoSave middleware is stub
- **GIVEN** AutoSave middleware is configured
- **WHEN** an action is dispatched
- **THEN** it SHALL pass the action through without saving (Stage 3/5 feature)

### Requirement: Action types for game operations
The system SHALL provide concrete action classes for common game operations.

#### Scenario: GraphTransitionAction
- **GIVEN** `GraphTransitionAction` is instantiated with `{"to": "node_id"}`
- **WHEN** processed by the graph reducer
- **THEN** the entity's current_node_id SHALL be updated to the target node

#### Scenario: EndGameAction
- **GIVEN** `EndGameAction` is instantiated
- **WHEN** processed
- **THEN** the session SHALL be marked as ended

### Requirement: Invalid action type raises error
The system SHALL raise an appropriate error when an action with invalid type is dispatched.

#### Scenario: Invalid action type
- **GIVEN** an action with unrecognized type
- **WHEN** dispatched
- **THEN** an appropriate error SHALL be raised
