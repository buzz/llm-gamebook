from collections.abc import Iterable
from dataclasses import dataclass
from typing import TYPE_CHECKING, cast

from pydantic import BaseModel

from llm_gamebook.schema.base import Slug
from llm_gamebook.story.entity import BaseStoryEntity
from llm_gamebook.utils import EventBusMixin

if TYPE_CHECKING:
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
    name: Slug
    params: BaseModel | None


@dataclass
class EntityType:
    slug: Slug
    name: str
    instructions: str | None
    traits: list[Trait] | None
    instances: list[BaseStoryEntity]
    cls: type[BaseStoryEntity]

    def get_template_context(self) -> dict[str, object]:
        return {
            "slug": self.slug,
            "name": self.name,
            "instructions": self.instructions,
            "traits": [trait.name for trait in self.traits or ()],
            "instances": self.instances,
        }

    def get_tools(self) -> "Iterable[StoryTool]":
        for instance in self.instances:
            yield from instance.get_tools()


class StoryState(EventBusMixin):
    def __init__(
        self,
        entity_types: dict[Slug, EntityType],
        title: str,
        author: str | None = None,
        description: str | None = None,
    ) -> None:
        super().__init__()
        self.entity_types = entity_types
        self.title = title
        self.author = author
        self.description = description

        # Let instances register events
        for instance in self.all_instances():
            instance.register_events(self)

        self.emit("init")

    def all_instances(self) -> Iterable[BaseStoryEntity]:
        for et in self.entity_types.values():
            yield from et.instances

    def get_entity_type(self, entity_type_slug: Slug) -> EntityType:
        try:
            return self.entity_types[entity_type_slug]
        except KeyError as err:
            msg = f"Entity type not found: {entity_type_slug}"
            raise EntityTypeNotFoundError(msg) from err

    def get_instance[T: BaseStoryEntity](
        self, slug: Slug, entity_type_slug: Slug, instance_type: type[T]
    ) -> T:
        try:
            entity_type = self.get_entity_type(entity_type_slug)
        except EntityTypeNotFoundError as err:
            msg = f"Invalid entity type: {entity_type_slug}"
            raise InstanceNotFoundError(msg) from err

        try:
            instance = next(ins for ins in entity_type.instances if ins.slug == slug)
        except StopIteration as err:
            msg = f"Instance not found: {slug}"
            raise InstanceNotFoundError(msg) from err

        return cast("T", instance)

    def get_trait_params[T: BaseModel](
        self,
        entity_type_slug: Slug,
        trait_slug: str,
        model: type[T],
    ) -> T:
        try:
            entity_type = self.get_entity_type(entity_type_slug)
        except EntityTypeNotFoundError as err:
            msg = f"Invalid entity type: {entity_type_slug}"
            raise TraitNotFoundError(msg) from err

        try:
            params = next(t for t in (entity_type.traits or ()) if t.name == trait_slug).params
        except StopIteration as err:
            msg = f"Trait not found: {trait_slug}"
            raise TraitNotFoundError(msg) from err

        if params is None:
            msg = f"Trait {trait_slug} has no parameters"
            raise TypeError(msg)

        return cast("T", params)
