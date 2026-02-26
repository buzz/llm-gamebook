# Story List UI

## ADDED Requirements

### Requirement: Stories page

The frontend SHALL provide a stories listing page at `/stories`.

#### Scenario: Navigate to stories

- **WHEN** a user navigates to `/stories`
- **THEN** the system SHALL display a list of all available stories
- **AND** each story SHALL be displayed as a card

#### Scenario: Loading state

- **WHEN** stories are being loaded
- **THEN** the system SHALL display a loading indicator

#### Scenario: Error state

- **WHEN** the stories API returns an error
- **THEN** the system SHALL display an error message with retry option

### Requirement: Story card component

Each story SHALL be displayed as a card.

#### Scenario: Story card display

- **WHEN** a story is rendered
- **THEN** the card SHALL display: title, description, source badge

#### Scenario: Source badge styling

- **WHEN** a story has `source: "example"`
- **THEN** the badge SHALL display "Example"
- **WHEN** a story has `source: "user"`
- **THEN** the badge SHALL display "My Story"

### Requirement: Play story action

Users SHALL be able to play a story from the list.

#### Scenario: Play button

- **WHEN** a user clicks "Play" on a story
- **THEN** the system SHALL create a new session with that story
- **AND** navigate to the player page

### Requirement: Navigation to stories

#### Scenario: Stories link in navbar

- **WHEN** the navbar is displayed
- **THEN** a "Stories" link SHALL be visible linking to `/stories`

## API

### Components

- `StoryList.tsx` - Page component
- `StoryCard.tsx` - Card component
- `StorySourceBadge.tsx` - Badge component

### Routes

```
/stories -> StoryList
```
