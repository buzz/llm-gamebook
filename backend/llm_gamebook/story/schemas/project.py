from collections.abc import Mapping
from enum import StrEnum, auto
from pathlib import Path
from typing import Annotated, Self, overload

import yaml
from pydantic import AfterValidator, BaseModel, Field, PrivateAttr

from llm_gamebook.constants import PROJECT_FILENAME
from llm_gamebook.story.errors import (
    EntityNotFoundError,
    EntityTypeNotFoundError,
    ProjectExistsError,
)
from llm_gamebook.story.schemas.entity import BaseEntity, EntityType, EntityTypeDefinition

from .validators import is_valid_project_id


class ProjectSource(StrEnum):
    EXAMPLE = auto()
    LOCAL = auto()


type ProjectId = Annotated[str, AfterValidator(is_valid_project_id)]


class ProjectDefinition(BaseModel):
    """Gamebook project definition loaded from external file."""

    id: ProjectId = Field(exclude=True)
    """The project ID in the format `namespace/name`."""

    source: ProjectSource = Field(exclude=True)
    """The project source type."""

    title: str
    """The project title."""

    author: str | None = None
    """The project author."""

    description: str | None
    """The project description."""

    image: str | None = Field(exclude=True, default=None)
    """The project image."""

    entity_types: list[EntityTypeDefinition] = Field(default_factory=list)
    """Definition of entity types."""

    def __str__(self) -> str:
        return f'<{type(self).__name__} id="{self.id}" title="{self.title}" source="{self.source}">'

    @property
    def namespace(self) -> str:
        return self.id.split("/", 1)[0]

    @property
    def name(self) -> str:
        return self.id.split("/", 1)[1]

    def save(self, save_path: Path) -> None:
        try:
            save_path.mkdir(parents=True)
        except FileExistsError as e:
            msg = f"Project '{self.id}' already exists"
            raise ProjectExistsError(msg) from e

        yaml_path = save_path / PROJECT_FILENAME
        yaml_path.write_text(yaml.dump(self.model_dump()))

    @classmethod
    def from_path(cls, project_path: Path) -> Self:
        namespace = project_path.parts[-2]
        name = project_path.parts[-1]
        project_filepath = project_path / PROJECT_FILENAME

        try:
            data = yaml.safe_load(project_filepath.read_text())
        except FileNotFoundError as err:
            msg = f"Project file not found: {project_filepath}"
            raise FileNotFoundError(msg) from err

        return cls.model_validate(
            {
                **data,
                "id": f"{namespace}/{name}",
                "source": ProjectSource.LOCAL,
            },
            strict=True,
        )


class Project(ProjectDefinition):
    """Runtime representation of a gamebook project."""

    _entity_type_map: Mapping[str, EntityType] = PrivateAttr()

    @property
    def entity_type_map(self) -> Mapping[str, EntityType]:
        return self._entity_type_map

    def get_template_context(self) -> Mapping[str, object]:
        return {
            "title": self.title,
            "description": self.description,
            "author": self.author,
            "entity_types": [et.get_template_context() for et in self._entity_type_map.values()],
        }

    def get_entity_type(self, entity_type_id: str) -> EntityType:
        try:
            return self.entity_type_map[entity_type_id]
        except KeyError as err:
            msg = f"Entity type not found: {entity_type_id}"
            raise EntityTypeNotFoundError(msg) from err

    @overload
    def get_entity(self, entity_id: str) -> BaseEntity: ...
    @overload
    def get_entity[T: BaseEntity](self, entity_id: str, model: type[T]) -> T: ...
    def get_entity[T: BaseEntity](
        self, entity_id: str, model: type[T] | None = None
    ) -> BaseEntity | T:
        try:
            entity = next(
                e
                for entity_type in self.entity_type_map.values()
                for e in entity_type.entity_map.values()
                if e.id == entity_id
            )
        except StopIteration as err:
            msg = f"Entity not found: {entity_id}"
            raise EntityNotFoundError(msg) from err

        if not isinstance(entity, model or BaseEntity):
            msg = f"Entity has unexpected type: {type(entity).__name__}"
            raise TypeError(msg)

        return entity

    @classmethod
    def from_path(cls, project_path: Path) -> Self:
        project_def = super().from_path(project_path)
        return cls.from_definition(project_def)

    @classmethod
    def from_data(cls, data: object) -> Self:
        project_def = super().model_validate(data, strict=True)
        return cls.from_definition(project_def)

    @classmethod
    def from_definition(cls, project_def: ProjectDefinition) -> Self:
        """Initialize runtime project from definition."""
        project = cls.model_validate(project_def, from_attributes=True)

        entity_types = (EntityType.from_definition(et, project) for et in project_def.entity_types)
        project._entity_type_map = {et.id: et for et in entity_types}

        for entity_type in project.entity_type_map.values():
            entity_type.post_init()

        return project
