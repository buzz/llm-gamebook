# Story API

## ADDED Requirements

### Requirement: List stories endpoint

The system SHALL provide an endpoint to list all stories.

#### Scenario: Successful list

- **WHEN** a client requests `GET /api/stories`
- **THEN** the system SHALL return HTTP 200
- **AND** the response SHALL contain a list of stories with count

#### Scenario: Filter by source

- **WHEN** a client requests `GET /api/stories?source=example`
- **THEN** the system SHALL return only stories from the specified source

### Requirement: Get story details endpoint

The system SHALL provide an endpoint to get story details.

#### Scenario: Successful get

- **WHEN** a client requests `GET /api/stories/{id}`
- **THEN** the system SHALL return HTTP 200 with story details
- **AND** the response SHALL include the story's entity types

#### Scenario: Story not found

- **WHEN** a client requests a non-existent story ID
- **THEN** the system SHALL return HTTP 404

### Requirement: Create empty story endpoint

The system SHALL provide an endpoint to create a new empty story.

#### Scenario: Create empty story

- **WHEN** a client requests `POST /api/stories` with `{ "name": "user/my-story", "title": "My Story" }`
- **THEN** the system SHALL create directory `STORIES_DIR/user/my-story/`
- **AND** the system SHALL create `llm-gamebook.yaml` with title and empty entity_types
- **AND** the system SHALL return HTTP 201 with the created story

#### Scenario: Invalid story name format

- **WHEN** a client provides an invalid name (not `namespace/story` format)
- **THEN** the system SHALL return HTTP 400 with validation error

#### Scenario: Story already exists

- **WHEN** a client tries to create a story that already exists
- **THEN** the system SHALL return HTTP 409 Conflict

### Requirement: Delete story endpoint

The system SHALL provide an endpoint to delete a story.

#### Scenario: Delete story

- **WHEN** a client requests `DELETE /api/stories/{id}`
- **THEN** the system SHALL delete the directory, e.g. `STORIES_DIR/user/my-story/`
- **AND** the system SHALL return HTTP 200

#### Scenario: Invalid story name format

- **WHEN** a client provides an invalid name (not `namespace/story` format)
- **THEN** the system SHALL return HTTP 400 with validation error

#### Scenario: Story not found

- **WHEN** a client requests a non-existent story ID
- **THEN** the system SHALL return HTTP 404

### Requirement: Story ID in sessions

Sessions SHALL reference stories by ID.

#### Scenario: Create session with story

- **WHEN** a client creates a session with `POST /api/sessions` including `story_id`
- **THEN** the engine SHALL load the specified story

## API

### Endpoints

```
GET    /api/stories              -> Stories
GET    /api/stories?source={str} -> Stories
GET    /api/stories/{id}         -> StoryDetail
POST   /api/stories              -> Story (201 Created)
DELETE /api/stories/{id}         -> 200
```

### Schemas

```typescript
interface StoryCreate {
  name: string;      // "user/my-story"
  title: string;
  description?: string;
}

interface Stories {
  data: Story[];
  count: number;
}

interface Story {
  name: string;      // "buzz/broken-bulb"
  title: string;
  description?: string;
  source: "example" | "user";
  is_editable: boolean;
}

interface StoryDetail extends Story {
  entity_types: EntityTypeSummary[];
}
```
