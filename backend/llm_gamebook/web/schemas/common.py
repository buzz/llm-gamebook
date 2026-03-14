from llm_gamebook.web.schemas.base import CamelCasedBaseModel


class ServerMessage(CamelCasedBaseModel):
    message: str
