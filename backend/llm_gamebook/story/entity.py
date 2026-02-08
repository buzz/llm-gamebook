from collections.abc import Iterable, Mapping, Sequence
from typing import TYPE_CHECKING, Self, overload

from pydantic import BaseModel, PrivateAttr, PydanticUndefinedAnnotation, create_model
from pydantic_ai.tools import ObjectJsonSchema

from llm_gamebook.schema.entity import EntityDefinition, EntityTypeDefinition

from .errors import EntityNotFoundError, TraitNotFoundError
from .trait_registry import trait_registry

if TYPE_CHECKING:
    from .project import Project
    from .types import StoryTool

type EntityProperty = Sequence[BaseEntity] | BaseEntity | str | bool | int | float


class BaseEntity(EntityDefinition):
    """Base class for all story entities.

    Extendable via mixin traits to add behavior and properties.
    """

    entity_type: "EntityType"
    project: "Project"

    def get_template_context(self) -> Mapping[str, object]:
        return {
            "id": self.id,
            "entity_type_id": self.entity_type.id,
        }

    def get_tools(self) -> "Iterable[StoryTool]":
        """Return instance's tools."""
        return ()

    def post_init(self) -> None:
        pass

    @staticmethod
    def _update_schema_descriptions(schema: ObjectJsonSchema, descriptions: dict[str, str]) -> None:
        """Update tool definition with custom property descriptions."""
        for key, descr in descriptions.items():
            try:
                schema["properties"][key]["description"] = descr
            except KeyError as err:
                msg = f"Property {key} not in argument for function {{trans_func.name}}"
                raise ValueError(msg) from err

    @classmethod
    def from_definition(
        cls,
        entity_def: "EntityDefinition",
        entity_type: "EntityType",
        entity_cls: type[Self],
        project: "Project",
    ) -> Self:
        """Create an entity from a definition."""
        kwargs = {
            # EntityDefinition
            **entity_def.model_dump(),
            # BaseEntity
            "entity_type": entity_type,
            "project": project,
            # Trait mixins
            **(entity_def.model_extra or {}),
        }

        # Instantiate entity
        try:
            return entity_cls(**kwargs)
        except TypeError as err:
            if "object.__init__() takes exactly one argument" in str(err):
                msg = f"You may have specified unknown properties for the entity: {entity_def}"
                raise ValueError(msg) from err
            raise


class EntityType(EntityTypeDefinition):
    """A entity type runtime object."""

    _entity_map: Mapping[str, BaseEntity] = PrivateAttr()
    """Mapping of IDs to instantiated runtime entities."""

    _trait_options_map: Mapping[str, BaseModel] = PrivateAttr()
    """Mapping of trait names to options."""

    @property
    def entity_map(self) -> Mapping[str, BaseEntity]:
        return self._entity_map

    @property
    def trait_options_map(self) -> Mapping[str, BaseModel]:
        return self._trait_options_map

    def get_template_context(self) -> Mapping[str, object]:
        return {
            "id": self.id,
            "name": self.name,
            "instructions": self.instructions,
            "traits": [t.name for t in self.traits],
            "entities": [entity.get_template_context() for entity in self.entity_map.values()],
        }

    def get_tools(self) -> "Iterable[StoryTool]":
        for entity in self.entity_map.values():
            yield from entity.get_tools()

    @overload
    def get_entity(self, entity_id: str) -> BaseEntity: ...
    @overload
    def get_entity[T: BaseEntity](self, entity_id: str, model: type[T]) -> T: ...
    def get_entity[T: BaseEntity](
        self, entity_id: str, model: type[T] | None = None
    ) -> BaseEntity | T:
        try:
            entity = self.entity_map[entity_id]
        except KeyError as err:
            msg = f"Entity not found: {entity_id}"
            raise EntityNotFoundError(msg) from err

        if not isinstance(entity, model or BaseEntity):
            msg = f"Entity has unexpected type: {type(entity).__name__}"
            raise TypeError(msg)

        return entity

    def get_trait_options[T: BaseModel](self, trait_id: str, model: type[T]) -> T:
        try:
            options = self.trait_options_map[trait_id]
        except StopIteration as err:
            msg = f"Trait options not found: {trait_id}"
            raise TraitNotFoundError(msg) from err

        if not isinstance(options, model):
            msg = f"Trait options model has unexpected type: {type(options).__name__}"
            raise TypeError(msg)

        return options

    @classmethod
    def from_definition(cls, entity_type_def: "EntityTypeDefinition", project: "Project") -> Self:
        """Build entity instances from definitions."""
        entity_cls, trait_options = cls._type_from_definition(entity_type_def, type(project))

        entity_type = cls(**entity_type_def.model_dump())
        entity_type._trait_options_map = trait_options

        entities = (
            BaseEntity.from_definition(entity_def, entity_type, entity_cls, project)
            for entity_def in entity_type_def.entities
        )
        entity_type._entity_map = {e.id: e for e in entities}

        return entity_type

    @classmethod
    def _type_from_definition(
        cls, entity_type_def: "EntityTypeDefinition", project_type: "type[Project]"
    ) -> tuple[type[BaseEntity], Mapping[str, BaseModel]]:
        """Build entity class from definitions."""
        trait_options: dict[str, BaseModel] = {}
        bases: list[type[BaseEntity]] = []

        # Add traits as base classes
        for trait_def in entity_type_def.traits:
            entry = trait_registry[trait_def.name]
            bases.append(entry.cls)

            # Validate trait options
            if entry.options_model:
                params = entry.options_model.model_validate(trait_def.options, strict=True)
                trait_options[trait_def.name] = params

        model: type[BaseEntity] = create_model(entity_type_def.id, __base__=(*bases, BaseEntity))

        try:
            # Help Pydantic resolve `Project`
            model.model_rebuild(_types_namespace={"Project": project_type})
        except PydanticUndefinedAnnotation as err:
            msg = f"Failed to build model: {model.__name__}"
            raise RuntimeError(msg) from err

        return model, trait_options

    def post_init(self) -> None:
        for entity in self.entity_map.values():
            entity.post_init()
