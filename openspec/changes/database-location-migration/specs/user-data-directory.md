# User Data Directory

## ADDED Requirements

### Requirement: Cross-platform user data directory

The application must provide a consistent interface for accessing the platform-standard user data directory.

#### Scenario: Directory path resolution

- **WHEN** the application initializes
- **THEN** `USER_DATA_DIR` must resolve to the platform-standard location:
  - Linux: `~/.local/share/llm-gamebook/`
  - macOS: `~/Library/Application Support/llm-gamebook/`
  - Windows: `%APPDATA%\llm-gamebook\`

#### Scenario: Directory creation

- **WHEN** the application starts
- **THEN** `USER_DATA_DIR` must be created if it does not exist
- **AND** if creation fails, an explicit error must be raised

## API

### Module: `llm_gamebook.constants`

```python
from pathlib import Path
from typing import Final

import platformdirs

PROJECT_NAME: Final = "llm-gamebook"
USER_DATA_DIR: Final[Path] = Path(platformdirs.user_data_dir("llm-gamebook", appauthor=False))
```

## Dependencies

- `platformdirs>=4.0.0`
