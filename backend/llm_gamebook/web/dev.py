"""Dev server entrypoint."""

import os
from pathlib import Path

from .app import create_app

is_debug = os.getenv("LLM_GAMEBOOK_DEBUG", "True").lower() in {"1", "true", "yes"}
log_file = os.getenv("LLM_GAMEBOOK_LOG_FILE")

app = create_app(Path(log_file) if log_file else None, debug=is_debug)
