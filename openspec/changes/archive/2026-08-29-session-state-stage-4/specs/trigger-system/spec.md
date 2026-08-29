## ADDED Requirements

### Requirement: Trigger definitions in entity type schema
The system SHALL support trigger definitions in entity type YAML with name, condition, and args.

#### Scenario: Trigger defined in YAML
- **GIVEN** an entity type definition in YAML with triggers
- **WHEN** the project is loaded
- **THEN** triggers SHALL be parsed and stored on the entity type

#### Scenario: Trigger schema fields
- **GIVEN** a trigger definition
- **WHEN** parsed
- **THEN** it SHALL have: name (action type), condition (bool expression), args (action payload)

### Requirement: EntityType stores triggers
The system SHALL have EntityType store loaded triggers.

#### Scenario: EntityType has triggers list
- **GIVEN** an EntityType with trigger definitions
- **WHEN** accessed
- **THEN** it SHALL have a `triggers` property returning list of triggers

### Requirement: Trigger evaluation middleware
The system SHALL implement TriggerEval middleware that evaluates triggers after agent steps.

#### Scenario: Middleware evaluates triggers
- **GIVEN** TriggerEval middleware configured in store
- **WHEN** an action is dispatched
- **THEN** it SHALL evaluate all triggers against current state
- **AND** dispatch actions for triggers with true conditions

#### Scenario: Triggers evaluate after state changes
- **GIVEN** user actions that change state in a step
- **WHEN** triggers are evaluated
- **THEN** triggers SHALL see the final state after user actions

#### Scenario: Multiple triggers fire
- **GIVEN** multiple triggers with true conditions
- **WHEN** evaluated
- **THEN** all true triggers SHALL fire in YAML order

### Requirement: Trigger conditions use BoolExprEvaluator
The system SHALL evaluate trigger conditions using BoolExprEvaluator with effective field values.

#### Scenario: Condition evaluates to true
- **GIVEN** a trigger with condition `=player.has_visited('village')`
- **AND** player has visited village (in effective state)
- **WHEN** trigger is evaluated
- **THEN** the condition SHALL return true
- **AND** the trigger action SHALL be dispatched

#### Scenario: Condition evaluates to false
- **GIVEN** a trigger with condition `=player.has_visited('village')`
- **AND** player has NOT visited village
- **WHEN** trigger is evaluated
- **THEN** the condition SHALL return false
- **AND** no action SHALL be dispatched

#### Scenario: Condition uses dynamic field reference
- **GIVEN** a trigger with condition `=player.current_node_id == 'village'`
- **WHEN** evaluated
- **THEN** it SHALL use effective field value (session override or project default)

### Requirement: Invalid condition raises error
The system SHALL raise an error when a trigger condition has invalid syntax.

#### Scenario: Invalid condition syntax
- **GIVEN** a trigger with invalid condition expression
- **WHEN** the trigger is evaluated
- **THEN** an appropriate error SHALL be raised with descriptive message

### Requirement: Trigger action dispatch
The system SHALL dispatch trigger actions with configured args when conditions are true.

#### Scenario: Trigger dispatches action with args
- **GIVEN** a trigger with name `graph/transition` and args `{"to": "unlock_ending"}`
- **WHEN** the condition is true
- **THEN** it SHALL dispatch GraphTransitionAction with payload from args

### Requirement: Prevent trigger infinite loops
The system SHALL prevent triggers from causing infinite dispatch loops.

#### Scenario: Same action type not re-dispatched
- **GIVEN** a trigger that would dispatch the same action type as just executed
- **WHEN** evaluated
- **THEN** it SHALL NOT re-dispatch that action type
