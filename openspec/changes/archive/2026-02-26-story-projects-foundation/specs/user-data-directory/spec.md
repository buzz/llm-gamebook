# User Data Directory

## MODIFIED Requirements

### Requirement: Cross-platform user data directory

The application must provide a consistent interface for accessing the platform-standard user data directory.

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

## API

### Module: `llm_gamebook.constants`

```python
from pathlib import Path
from typing import Final

import platformdirs

PROJECT_NAME: Final = "llm-gamebook"
USER_DATA_DIR: Final[Path] = Path(platformdirs.user_data_dir(PROJECT_NAME, appauthor=False))

STORIES_DIR: Final[Path] = USER_DATA_DIR / "stories"
EXAMPLES_DIR: Final[Path] = Path(__file__).parent.parent.parent.parent / "examples"
```

## Dependencies

- `platformdirs>=4.0.0` (existing)
