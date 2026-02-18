## ADDED Requirements

### Requirement: Templates receive EntityView proxies, not raw entities
The system SHALL ensure that Jinja2 templates access entities through `EntityView` proxies rather than raw entity objects.

#### Scenario: Template accesses entity through view
- **GIVEN** a Jinja2 template rendering with `TemplateContext`
- **WHEN** the template accesses an entity field via `entity.field`
- **THEN** the access SHALL go through `EntityView.__getattr__`
- **AND** session-aware resolution SHALL be applied

#### Scenario: Template sees identical attribute access syntax
- **GIVEN** a template using `{{ entity.name }}`
- **WHEN** rendered with `EntityView`-wrapped entities
- **THEN** the template syntax SHALL be unchanged from raw entity access
- **AND** the value SHALL be session-aware
