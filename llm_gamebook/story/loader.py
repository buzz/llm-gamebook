import abc
from pathlib import Path
from typing import TYPE_CHECKING, Any

import casefy
import yaml

from llm_gamebook.schema import GamebookProject
from llm_gamebook.schema.base import Slug
from llm_gamebook.schema.entity import EntityDefinition
from llm_gamebook.story.entity import BaseStoryEntity
from llm_gamebook.story.state import EntityType, StoryState, Trait
from llm_gamebook.story.traits.registry import trait_registry

if TYPE_CHECKING:
    from pydantic import BaseModel


class AbstractBaseLoader(abc.ABC):
    def __init__(self, project_path: Path) -> None:
        self._path = project_path

    @abc.abstractmethod
    def load(self) -> StoryState:
        raise NotImplementedError

    def _from_data(self, data: Any) -> StoryState:
        project = GamebookProject.model_validate(data, strict=True)
        return StoryState(
            self._compose_entity_types(project),
            project.title,
            project.author,
            project.description,
        )

    @classmethod
    def _compose_entity_types(cls, project: GamebookProject) -> dict[Slug, EntityType]:
        """Build entity classes from project definitions."""
        types: dict[Slug, EntityType] = {}
        for entity_def in project.entities:
            traits, bases = cls._compose_traits(entity_def)
            entity_cls = type(casefy.pascalcase(entity_def.slug), bases, {})
            instances = cls._create_instances(entity_def, entity_cls)

            types[entity_def.slug] = EntityType(
                slug=entity_def.slug,
                name=entity_def.name,
                instructions=entity_def.instructions,
                traits=traits,
                instances=instances,
                functions=entity_def.functions,
                cls=entity_cls,
            )

        return types

    @classmethod
    def _compose_traits(cls, entity_def: EntityDefinition) -> tuple[list[Trait], tuple[type, ...]]:
        traits: list[Trait] = []
        bases: list[type] = []

        for trait_spec in entity_def.traits:
            # Look up trait class
            entry = trait_registry[trait_spec.name]
            trait_cls = entry["class"]
            bases.append(trait_cls)
            param_model = entry["param_model"]

            # Validate trait parameters
            params: BaseModel | None = None
            if param_model:
                params = param_model.model_validate(trait_spec.params, strict=True)

            traits.append(Trait(trait_spec.name, params))

        return traits, (*bases, BaseStoryEntity)

    @classmethod
    def _create_instances(
        cls,
        entity_def: EntityDefinition,
        entity_cls: type[BaseStoryEntity],
    ) -> list[BaseStoryEntity]:
        instances: list[BaseStoryEntity] = []
        for instance_def in entity_def.instances:
            # Validate instance fields against trait constructor arg types
            for trait_spec in entity_def.traits:
                arg_model = trait_registry[trait_spec.name]["arg_model"]
                if arg_model:
                    arg_model.model_validate(instance_def.model_extra, strict=True)

            kwargs = {
                **instance_def.model_dump(),  # slug
                "entity_type_slug": entity_def.slug,
                **(instance_def.model_extra or {}),
            }
            instances.append(entity_cls(**kwargs))
        return instances


class YAMLLoader(AbstractBaseLoader):
    def load(self) -> StoryState:
        data = yaml.safe_load((self._path / "llm-gamebook.yaml").read_text())
        return self._from_data(data)
