from typing import Literal

from llm_gamebook.web.schemas.base import CamelCasedBaseModel


class UserSettings(CamelCasedBaseModel):
    chat_view: Literal["standard", "details", "debug"] = "standard"
    enter_submits_message: bool = True
