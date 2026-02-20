from pathlib import Path
from typing import Final

import platformdirs

PROJECT_NAME: Final = "llm-gamebook"
PROJECT_FILENAME: Final = f"{PROJECT_NAME}.yaml"
USER_DATA_PATH: Final[Path] = Path(platformdirs.user_data_dir(PROJECT_NAME, appauthor=False))
PROJECTS_PATH: Final[Path] = USER_DATA_PATH / "projects"
EXAMPLES_PATH: Final[Path] = Path(__file__).parent.parent.parent / "examples"
