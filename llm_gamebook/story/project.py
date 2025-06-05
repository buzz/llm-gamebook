from collections.abc import Mapping
from pathlib import Path
from typing import Any, Self, overload

import yaml
from pydantic import PrivateAttr

from llm_gamebook.constants import PROJECT_NAME
from llm_gamebook.schema.project import ProjectDefinition
from llm_gamebook.story.entity import BaseEntity, EntityType
from llm_gamebook.story.errors import EntityNotFoundError, EntityTypeNotFoundError


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
    def from_dir(cls, project_path: Path) -> Self:
        project_filepath = project_path / f"{PROJECT_NAME}.yaml"

        try:
            data = yaml.safe_load(project_filepath.read_text())
        except FileNotFoundError as err:
            msg = f"Project file not found: {project_filepath}"
            raise FileNotFoundError(msg) from err

        return cls.from_data(data)

    @classmethod
    def from_data(cls, data: Any) -> Self:
        project_def = ProjectDefinition.model_validate(data, strict=True)
        return cls.from_definition(project_def)

    @classmethod
    def from_definition(cls, project_def: ProjectDefinition) -> Self:
        project = cls(**project_def.model_dump())
        entity_types = (
            EntityType.from_definition(def_, project) for def_ in project_def.entity_types
        )
        project._entity_type_map = {et.id: et for et in entity_types}

        for entity_type in project.entity_type_map.values():
            entity_type.post_init()

        return project
