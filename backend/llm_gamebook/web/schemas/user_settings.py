from typing import Literal

from llm_gamebook.constants import DEFAULT_MAX_STATE_HISTORY
from llm_gamebook.web.schemas.base import CamelCasedBaseModel


class UserSettings(CamelCasedBaseModel):
    chat_view: Literal["standard", "details", "debug"] = "standard"
    enter_submits_message: bool = True
    max_state_history: int = DEFAULT_MAX_STATE_HISTORY
