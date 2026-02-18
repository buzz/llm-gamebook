# Template View System

## Purpose

This capability provides a view layer that wraps entities for Jinja2 templates, enabling session-aware attribute access without modifying template syntax.

## Requirements

### Requirement: EntityView provides session-aware attribute access
The system SHALL provide an `EntityView` class that wraps an entity and intercepts attribute access to return session-aware values.

#### Scenario: Access entity attribute through view
- **GIVEN** an entity with field `name = "default_name"` and no session override
- **WHEN** `EntityView(entity, ctx).name` is accessed
- **THEN** the value `"default_name"` SHALL be returned

#### Scenario: Session override takes precedence
- **GIVEN** an entity with field `name = "default_name"`
- **AND** session state has override `name = "override_name"`
- **WHEN** `EntityView(entity, ctx).name` is accessed
- **THEN** the override value `"override_name"` SHALL be returned

#### Scenario: Session field resolver takes precedence over session state
- **GIVEN** an entity with a `@session_field("current_node")` resolver
- **AND** session state has override for `current_node`
- **WHEN** `EntityView(entity, ctx).current_node` is accessed
- **THEN** the resolver method SHALL be called with StoryContext
- **AND** the resolver result SHALL be returned

#### Scenario: Nested entity is wrapped in EntityView
- **GIVEN** an entity with a field that returns another entity
- **WHEN** that field is accessed through `EntityView`
- **THEN** the returned entity SHALL be wrapped in a new `EntityView`

#### Scenario: List of entities is wrapped
- **GIVEN** an entity with a field that returns a list of entities
- **WHEN** that field is accessed through `EntityView`
- **THEN** each entity in the list SHALL be wrapped in `EntityView`

### Requirement: TemplateContext is the root view for Jinja2
The system SHALL provide a `TemplateContext` class that serves as the root context for Jinja2 templates.

#### Scenario: TemplateContext proxies project-level fields
- **GIVEN** a project with `title = "My Game"`
- **WHEN** `TemplateContext(story_context).title` is accessed
- **THEN** the project title SHALL be returned

#### Scenario: TemplateContext provides entity_types
- **GIVEN** a project with multiple entity types
- **WHEN** `TemplateContext(story_context).entity_types` is accessed
- **THEN** a list of `EntityTypeView` objects SHALL be returned

#### Scenario: EntityTypeView provides wrapped entities
- **GIVEN** an entity type with multiple entities
- **WHEN** `EntityTypeView.entities` is accessed
- **THEN** each entity SHALL be wrapped in `EntityView`

### Requirement: session_field decorator marks session-aware resolvers
The system SHALL provide a `@session_field(field_name)` decorator that marks a trait method as the session-aware resolver for a field.

#### Scenario: Decorator registers resolver in trait_registry
- **GIVEN** a trait class with method decorated `@session_field("current_node")`
- **WHEN** the trait is registered with `trait_registry.register()`
- **THEN** the registry SHALL map `"current_node"` to the resolver method name

#### Scenario: Resolver receives StoryContext
- **GIVEN** a `@session_field("enabled")` resolver method on a trait
- **WHEN** the resolver is invoked by `EntityView`
- **THEN** the StoryContext SHALL be passed as the only argument

### Requirement: reducer decorator marks action handlers
The system SHALL provide a `@reducer(action_name)` decorator that marks a trait method as a reducer for a specific action.

#### Scenario: Decorator registers reducer in trait_registry
- **GIVEN** a trait class with method decorated `@reducer("graph/transition")`
- **WHEN** the trait is registered with `trait_registry.register()`
- **THEN** the registry SHALL map `"graph/transition"` to the reducer method name

### Requirement: No circular imports between components
The system SHALL maintain a clean import structure with no circular dependencies.

#### Scenario: Traits do not import StoryContext at runtime
- **GIVEN** a trait file with `@session_field` methods
- **WHEN** the module is imported
- **THEN** `StoryContext` SHALL only be imported under `TYPE_CHECKING`
- **AND** method signatures SHALL use string annotations for `StoryContext`

#### Scenario: template_view imports context, not vice versa
- **GIVEN** the module structure
- **WHEN** imports are analyzed
- **THEN** `template_view.py` SHALL import from `context.py`
- **AND** `context.py` SHALL NOT import from `template_view.py`
