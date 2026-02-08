from pathlib import Path
from typing import Final

import platformdirs

PROJECT_NAME: Final = "llm-gamebook"
USER_DATA_DIR: Final[Path] = Path(platformdirs.user_data_dir(PROJECT_NAME, appauthor=False))
