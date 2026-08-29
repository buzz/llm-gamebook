# Story Discovery

## Purpose

Discovers stories from two directories — example stories bundled with the app and user stories under `STORIES_DIR` — deriving story names from the `{namespace}/{story}` directory path, and marking example stories read-only and user stories editable.

## Requirements

### Requirement: List stories from multiple sources

The system SHALL list stories from two directories: examples (bundled with app) and user stories.

#### Scenario: List all stories

- **WHEN** a client requests `GET /api/stories`
- **THEN** the system SHALL return stories from both directories
- **AND** each story SHALL include its source type (example or user)

#### Scenario: Empty story list

- **WHEN** no stories exist
- **THEN** the system SHALL return an empty list with count 0

### Requirement: Story name derived from path

Story names SHALL be derived from directory structure.

#### Scenario: Name derivation

- **WHEN** a story is discovered at `{base}/{namespace}/{story}/`
- **THEN** the story name SHALL be `{namespace}/{story}`
- **AND** the story ID SHALL be `{source}:{namespace}/{story}`

#### Scenario: Example story discovery

- **WHEN** the application scans `examples/`
- **THEN** the system SHALL discover all directories matching `examples/{namespace}/{story}/` containing `llm-gamebook.yaml`
- **AND** each story SHALL have `source: "example"`

#### Scenario: User story discovery

- **WHEN** the application scans user stories directory
- **THEN** the system SHALL discover all directories matching `STORIES_DIR/{namespace}/{story}/` containing `llm-gamebook.yaml`
- **AND** each story SHALL have `source: "user"`

### Requirement: Story source properties
Stories SHALL expose their source type, which determines whether the story is editable.

#### Scenario: Example stories are read-only

- **WHEN** a story has `source: "example"`
- **THEN** the story SHALL be marked as read-only (`is_editable: false`)

#### Scenario: User stories are editable

- **WHEN** a story has `source: "user"`
- **THEN** the story SHALL be marked as editable (`is_editable: true`)
