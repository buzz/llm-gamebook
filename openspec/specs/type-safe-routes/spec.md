## ADDED Requirements

### Requirement: Centralized route definitions
All frontend routes SHALL be defined in a single source of truth (`frontend/src/routes.ts`) using path strings with named parameters (e.g., `/gamebook/:namespace/:name`).

#### Scenario: Route name autocomplete
- **WHEN** developer types `routes.` in their IDE
- **THEN** they see autocomplete suggestions for all available route names (e.g., `home`, `gamebook.view`, `editor.edit`)

#### Scenario: Single path definition
- **WHEN** a route path needs to change (e.g., `/gamebook/:id` → `/books/:id`)
- **THEN** the change is made in one place (the central route definition)

### Requirement: Type-safe URL building
The system SHALL provide a `buildUrl(routeName, params)` function that constructs URLs from route names and parameters with type checking.

#### Scenario: Building URL with required parameters
- **WHEN** calling `buildUrl('gamebook.view', { namespace: 'foo', name: 'bar' })`
- **THEN** the function returns `/gamebook/foo/bar`
- **AND** TypeScript validates that both `namespace` and `name` parameters are provided

#### Scenario: Building URL without parameters
- **WHEN** calling `buildUrl('home')` for a static route
- **THEN** the function returns `/`
- **AND** TypeScript does not require a second argument

#### Scenario: Missing required parameters
- **WHEN** calling `buildUrl('gamebook.view', { namespace: 'foo' })` without `name`
- **THEN** TypeScript raises a type error at compile time

#### Scenario: Extra parameters
- **WHEN** calling `buildUrl('home', { extra: 'param' })` with unnecessary parameters
- **THEN** TypeScript raises a type error at compile time

### Requirement: Auto-generated wouter routes
The system SHALL auto-generate the wouter route array from central definitions, converting path strings to regex patterns where needed.

#### Scenario: Static route conversion
- **WHEN** wouter routes are generated from `/gamebook/new`
- **THEN** the path remains as string `/gamebook/new`

#### Scenario: Dynamic route conversion
- **WHEN** wouter routes are generated from `/gamebook/:namespace/:name`
- **THEN** the path is converted to a RegExp pattern that captures both parameters

#### Scenario: Route synchronization
- **WHEN** a new route is added to central definitions
- **THEN** it automatically appears in the wouter routes array without manual updates

### Requirement: Link component integration
Components SHALL use `buildUrl()` instead of template literals for constructing route paths in `Link` components.

#### Scenario: Using buildUrl in Link
- **WHEN** a component renders `<Link to={buildUrl('gamebook.view', { namespace, name })} />`
- **THEN** the link navigates to the correct path
- **AND** the route name and parameters are type-checked

#### Scenario: Refactoring safety
- **WHEN** a route path changes in central definitions
- **THEN** all `buildUrl()` calls automatically use the new path
- **AND** TypeScript flags any calls with incorrect parameters

### Requirement: Route parameter validation
The system SHALL validate that route parameters are non-empty strings.

#### Scenario: Empty parameter
- **WHEN** calling `buildUrl('gamebook.view', { namespace: '', name: 'bar' })`
- **THEN** the function either rejects empty parameters or encodes them safely

#### Scenario: Special characters
- **WHEN** calling `buildUrl('gamebook.view', { namespace: 'foo/bar', name: 'bar' })` with slashes
- **THEN** the function properly encodes the parameter value
