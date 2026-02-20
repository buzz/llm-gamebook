from collections.abc import Sequence

from pydantic import BaseModel

from llm_gamebook.story.schemas import ProjectId, ProjectSource
from llm_gamebook.story.schemas.entity import EntityTypeDefinition


class ProjectBasic(BaseModel):
    id: ProjectId
    """Unique project ID in the format `namespace/name`."""

    source: ProjectSource
    """The project source type."""

    title: str
    """Project title."""

    author: str | None = None
    """The project author."""

    description: str | None = None
    """Optional project description."""


class ProjectDetail(ProjectBasic):
    entity_types: list[EntityTypeDefinition]


class ProjectCreate(ProjectBasic):
    """Create fields for a project."""


class Projects(BaseModel):
    """A list of projects."""

    data: Sequence[ProjectBasic]
    count: int
