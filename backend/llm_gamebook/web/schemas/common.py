from pydantic import BaseModel


class ServerMessage(BaseModel):
    message: str
