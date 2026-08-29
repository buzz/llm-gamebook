## MODIFIED Requirements

### Requirement: StoryContext integrates session and project state
The system SHALL update `StoryContext` to hold both project and session state, providing access to effective field values.

Effective field resolution SHALL follow this precedence:

1. session state override (a stored plain value)
2. dynamic evaluation, when the project default is a dynamic expression
3. the static project default

#### Scenario: Effective field returns project default
- **GIVEN** a `StoryContext` with a project containing an entity with field `x = "default"`
- **AND** no session state override for field `x`
- **WHEN** `get_effective_field(entity_id, field_name)` is called
- **THEN** the project default value SHALL be returned

#### Scenario: Effective field returns session override
- **GIVEN** a `StoryContext` with a project containing an entity with field `x = "default"`
- **AND** session state override sets `x = "override"`
- **WHEN** `get_effective_field(entity_id, field_name)` is called
- **THEN** the override value `"override"` SHALL be returned

#### Scenario: Effective field evaluates dynamic default
- **GIVEN** a `StoryContext` with a project containing an entity with dynamic field `x = "=y + 1"`
- **AND** no session state override for field `x`
- **WHEN** `get_effective_field(entity_id, field_name)` is called
- **THEN** the value SHALL be the expression evaluated against the current effective state

#### Scenario: Session override shadows dynamic default
- **GIVEN** a `StoryContext` with a project containing a dynamic field `x`
- **AND** session state override sets `x = 42`
- **WHEN** `get_effective_field(entity_id, field_name)` is called
- **THEN** the override value `42` SHALL be returned without evaluating the expression

#### Scenario: Set field through StoryContext
- **GIVEN** a `StoryContext` instance
- **WHEN** `set_field(entity_id, field_name, value)` is called
- **THEN** the value SHALL be stored in session state

#### Scenario: Setting a dynamic field is an error
- **GIVEN** a `StoryContext` instance for a project where field `x` is dynamic
- **WHEN** `set_field(entity_id, field_name, value)` is called for field `x`
- **THEN** an error SHALL be raised identifying the field and that dynamic fields are read-only
