# User Data Directory

## Purpose

Provides the platform-standard user data directory via `platformdirs` (`USER_DATA_DIR`), created on startup, along with constants for user story (`STORIES_DIR`) and example story (`EXAMPLES_DIR`) locations.

## Requirements

### Requirement: Cross-platform user data directory

The application MUST provide a consistent interface for accessing the platform-standard user data directory.

#### Scenario: Directory path resolution

- **WHEN** the application initializes
- **THEN** `USER_DATA_DIR` must resolve to the platform-standard location:
  - Linux: `~/.local/share/llm-gamebook/`
  - macOS: `~/.local/share/llm-gamebook/`
  - Windows: `%APPDATA%\llm-gamebook\`

#### Scenario: Directory creation

- **WHEN** the application starts
- **THEN** `USER_DATA_DIR` must be created if it does not exist
- **AND** if creation fails, an explicit error must be raised

### Requirement: Story directories

The application SHALL provide constants for story directories.

#### Scenario: Stories directory constant

- **WHEN** the application needs user story paths
- **THEN** `STORIES_DIR` SHALL resolve to `USER_DATA_DIR / "stories"`
- **AND** the directory SHALL be created on startup if it does not exist

#### Scenario: Examples directory constant

- **WHEN** the application needs example story paths
- **THEN** `EXAMPLES_DIR` SHALL resolve to the examples directory within the application package
- **AND** the path SHALL work in both development and installed environments
