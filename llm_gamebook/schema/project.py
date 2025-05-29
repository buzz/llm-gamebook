from pydantic import BaseModel

from llm_gamebook.schema.entity import EntityDefinition


class GamebookProject(BaseModel):
    """A gamebook project."""

    title: str
    """The project title."""

    author: str | None = None
    """The project author."""

    description: str | None
    """The project description."""

    entities: list[EntityDefinition]
    """List of entity types."""

    def __str__(self) -> str:
        return f'<{type(self).__name__} title="{self.title}">'
