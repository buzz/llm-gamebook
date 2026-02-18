# Story Discovery

## ADDED Requirements

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

#### Scenario: Example stories are read-only

- **WHEN** a story has `source: "example"`
- **THEN** the story SHALL be marked as read-only (`is_editable: false`)

#### Scenario: User stories are editable

- **WHEN** a story has `source: "user"`
- **THEN** the story SHALL be marked as editable (`is_editable: true`)

## API

### Endpoint: `GET /api/stories`

Response:
```json
{
  "data": [
    {
      "id": "example:buzz/broken-bulb",
      "name": "buzz/broken-bulb",
      "title": "The Broken Bulb",
      "description": "A simple example story",
      "source": "example",
      "is_editable": false
    }
  ],
  "count": 1
}
```
