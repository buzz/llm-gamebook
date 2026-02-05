from uuid import UUID, uuid4

from sqlalchemy import Column, Enum, Text
from sqlmodel import Field, Relationship, SQLModel

from llm_gamebook.providers import ModelProvider

from .session import Session


class ModelConfigBase(SQLModel):
    name: str = Field(description="User-friendly display name for the model configuration")
    provider: ModelProvider = Field(sa_column=Column(Enum(ModelProvider)))
    model_name: str
    base_url: str | None = None
    api_key: str | None = Field(default=None, sa_column=Column(Text))
    context_window: int
    max_tokens: int
    temperature: float
    top_p: float
    presence_penalty: float
    frequency_penalty: float
    # TODO
    # logitBias: unknown
    # extraHeaders: unknown
    # extraBody: unknwon


class ModelConfig(ModelConfigBase, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    sessions: list[Session] = Relationship(
        back_populates="config",
        sa_relationship_kwargs={"lazy": "selectin"},
    )
