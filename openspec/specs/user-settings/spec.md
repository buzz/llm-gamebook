# User Settings

## Purpose

Server-side persistence of single-user preferences (chat view, color theme, enter-key behavior) in a single `UserSettings` SQLite row, exposed through `GET /settings` and `PUT /settings`, with default values applied on first access.

## Requirements

### Requirement: User settings model stores user preferences

The system SHALL store user settings in a `UserSettings` model with fields for `id`, `chat_view`, `color_theme`, and `enter_submits_message`. The system SHALL maintain exactly one settings record for the single user.

#### Scenario: Create settings for first access
- **GIVEN** settings are accessed for the first time
- **WHEN** settings are accessed for the first time
- **THEN** a default `UserSettings` record is created with default values

#### Scenario: Settings uniquely identified
- **GIVEN** querying for settings
- **WHEN** settings are queried
- **THEN** exactly one `UserSettings` record is returned

### Requirement: Settings API endpoints for GET and PUT

The system SHALL provide `/settings` endpoints for reading and updating user settings.

#### Scenario: Get user settings
- **GIVEN** settings exist
- **WHEN** `GET /settings` is called
- **THEN** system returns the settings as JSON

#### Scenario: Update user settings
- **GIVEN** settings exist
- **WHEN** `PUT /settings` is called with valid JSON body
- **THEN** system updates the settings record and returns updated settings

### Requirement: Settings persistence in SQLite

Settings SHALL be persisted to SQLite database using SQLModel.

#### Scenario: Settings survive restart
- **GIVEN** user settings are saved
- **WHEN** server restarts
- **THEN** settings are restored from database

#### Scenario: Settings update persists
- **GIVEN** user settings exist
- **WHEN** settings are updated via API
- **THEN** database record is updated

### Requirement: Default settings for new users

New settings SHALL receive default values on first access.

#### Scenario: Default chat view
- **GIVEN** settings do not exist
- **WHEN** settings are accessed
- **THEN** `chat_view` defaults to `"standard"`

#### Scenario: Default enter key behavior
- **GIVEN** settings do not exist
- **WHEN** settings are accessed
- **THEN** `enter_submits_message` defaults to `true`
