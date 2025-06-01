from pydantic import BaseModel

from llm_gamebook.schema.entity import EntityTypeDefinition


class ProjectDefinition(BaseModel):
    """Gamebook project definition loaded from external file."""

    title: str
    """The project title."""

    author: str | None = None
    """The project author."""

    description: str | None
    """The project description."""

    entity_types: list[EntityTypeDefinition]
    """Definition of entity types."""

    def __str__(self) -> str:
        return f'<{type(self).__name__} title="{self.title}">'
