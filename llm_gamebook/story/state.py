from collections.abc import Mapping
from dataclasses import dataclass
from typing import TYPE_CHECKING, cast

from pydantic import BaseModel

from llm_gamebook.utils import EventBusMixin

if TYPE_CHECKING:
    from collections.abc import Iterable

    from llm_gamebook.schema.entity import FunctionSpec
    from llm_gamebook.story.entity import BaseStoryEntity
    from llm_gamebook.types import StoryTool


class StateNotFoundError(Exception):
    pass


class EntityTypeNotFoundError(StateNotFoundError):
    pass


class TraitNotFoundError(StateNotFoundError):
    pass


class InstanceNotFoundError(StateNotFoundError):
    pass


@dataclass
class Trait:
    id: str
    params: BaseModel | None


@dataclass
class EntityType:
    id: str
    name: str
    instructions: str | None
    traits: list[Trait] | None
    entities: "Mapping[str, BaseStoryEntity]"
    functions: "list[FunctionSpec] | None"

    def get_template_context(
        self, entities: "Mapping[str, BaseStoryEntity]"
    ) -> Mapping[str, object]:
        return {
            "id": self.id,
            "name": self.name,
            "instructions": self.instructions,
            "traits": [trait.id for trait in self.traits or ()],
            "entities": [
                entity.get_template_context(entities) for entity in self.entities.values()
            ],
        }

    def get_tools(self) -> "Iterable[StoryTool]":
        for entity in self.entities.values():
            yield from entity.get_tools()


class StoryState(EventBusMixin):
    def __init__(
        self,
        entity_types: Mapping[str, EntityType],
        title: str,
        author: str | None = None,
        description: str | None = None,
    ) -> None:
        super().__init__()
        self.entity_types = entity_types
        self.title = title
        self.author = author
        self.description = description

        # Let entities register events
        for entity in self.all_entities().values():
            entity.register_events(self)

        self.emit("init")

    def all_entities(self) -> "Mapping[str, BaseStoryEntity]":
        return {
            id_: entity
            for entity_type in self.entity_types.values()
            for id_, entity in entity_type.entities.items()
        }

    def get_entity_type(self, entity_type_id: str) -> EntityType:
        try:
            return self.entity_types[entity_type_id]
        except KeyError as err:
            msg = f"Entity type not found: {entity_type_id}"
            raise EntityTypeNotFoundError(msg) from err

    def get_entity[T: "BaseStoryEntity"](
        self, id_: str, entity_type_id: str, cast_type: type[T]
    ) -> T:
        try:
            entity_type = self.get_entity_type(entity_type_id)
        except EntityTypeNotFoundError as err:
            msg = f"Invalid entity type: {entity_type_id}"
            raise InstanceNotFoundError(msg) from err

        try:
            entity = entity_type.entities[id_]
        except StopIteration as err:
            msg = f"Instance not found: {id_}"
            raise InstanceNotFoundError(msg) from err

        return cast("T", entity)

    def get_trait_params[T: BaseModel](
        self, entity_type_id: str, trait_id: str, model: type[T]
    ) -> T:
        try:
            entity_type = self.get_entity_type(entity_type_id)
        except EntityTypeNotFoundError as err:
            msg = f"Invalid entity type: {entity_type_id}"
            raise TraitNotFoundError(msg) from err

        try:
            params = next(t for t in (entity_type.traits or ()) if t.id == trait_id).params
        except StopIteration as err:
            msg = f"Trait not found: {trait_id}"
            raise TraitNotFoundError(msg) from err

        if params is None:
            msg = f"Trait {trait_id} has no parameters"
            raise TypeError(msg)

        return cast("T", params)
