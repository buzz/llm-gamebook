from collections.abc import Iterator
from contextlib import suppress
from typing import TYPE_CHECKING

from .errors import EntityFieldNotFoundError, TraitNotFoundError
from .schemas import BaseEntity, EntityType
from .trait_registry import trait_registry

if TYPE_CHECKING:
    from .context import StoryContext


class EntityView:
    """Proxy wrapper for session-aware entity attribute access.

    Resolution order for attribute access:
    1. Session field resolver (via @session_field decorator)
    2. Session state direct field override
    3. Entity default attribute value
    """

    __slots__ = ("_entity", "_story_context")

    def __init__(self, entity: BaseEntity, story_context: "StoryContext") -> None:
        self._entity = entity
        self._story_context = story_context

    def __repr__(self) -> str:
        return f"EntityView({self._entity.id!r})"

    def __getattr__(self, name: str) -> object:
        if name.startswith("_"):
            raise AttributeError(name)

        entity = self._entity
        ctx = self._story_context

        # 1. Session field resolver

        for trait_cls in type(entity).__mro__:
            if trait_cls.__name__ in {"BaseEntity", "BaseModel"}:
                continue
            if trait_cls.__module__.startswith("pydantic"):
                continue

            try:
                entry = trait_registry.get_by_type(trait_cls)
            except TraitNotFoundError:
                continue
            else:
                if entry.session_fields and name in entry.session_fields:
                    method_name = entry.session_fields[name]
                    method = getattr(entity, method_name)
                    if not callable(method):
                        msg = f"Expected callable: {trait_cls.__name__}::{method_name}"
                        raise TypeError(msg)
                    result = method(ctx)
                    return self._wrap_if_needed(result)

        # 2. Session state

        with suppress(EntityFieldNotFoundError):
            return ctx.session_state.get_field(entity.id, name)

        # 3. Entity default

        try:
            result = getattr(entity, name)
            return self._wrap_if_needed(result)
        except AttributeError:
            msg = f"{type(entity).__name__}.{name}"
            raise AttributeError(msg) from None

    def __getitem__(self, name: str) -> object:
        return getattr(self, name)

    def _wrap_if_needed(self, value: object) -> object:
        """Wrap nested BaseEntity and list[BaseEntity] results in EntityView."""
        if isinstance(value, BaseEntity):
            return EntityView(value, self._story_context)
        if isinstance(value, list):
            return [self._wrap_if_needed(item) for item in value]
        return value


class EntityTypeView:
    """Proxy wrapper for EntityType with session-aware entity list."""

    __slots__ = ("_entity_type", "_story_context")

    def __init__(self, entity_type: EntityType, story_context: "StoryContext") -> None:
        self._entity_type = entity_type
        self._story_context = story_context

    def __repr__(self) -> str:
        return f"EntityTypeView({self._entity_type.id!r})"

    @property
    def id(self) -> str:
        return self._entity_type.id

    @property
    def name(self) -> str:
        return self._entity_type.name

    @property
    def instructions(self) -> str | None:
        return self._entity_type.instructions

    @property
    def traits(self) -> list[str]:
        return [t.name for t in self._entity_type.traits]

    @property
    def entities(self) -> list[EntityView]:
        return [EntityView(e, self._story_context) for e in self._entity_type.entity_map.values()]

    def __getattr__(self, name: str) -> object:
        if name.startswith("_"):
            raise AttributeError(name)
        return getattr(self._entity_type, name)

    def __getitem__(self, name: str) -> object:
        return getattr(self, name)


class TemplateContext:
    """Root view object passed to Jinja2 templates.

    Provides project-level field proxies and entity type accessors.
    """

    __slots__ = ("_project", "_story_context")

    _CONTEXT_KEYS = ("title", "description", "author", "entity_types")

    def __init__(self, story_context: "StoryContext") -> None:
        self._story_context = story_context
        self._project = story_context.project

    @property
    def title(self) -> str:
        return self._project.title

    @property
    def description(self) -> str | None:
        return self._project.description

    @property
    def author(self) -> str | None:
        return self._project.author

    @property
    def entity_types(self) -> list[EntityTypeView]:
        return [
            EntityTypeView(et, self._story_context) for et in self._project.entity_type_map.values()
        ]

    def __getattr__(self, name: str) -> object:
        if name.startswith("_"):
            raise AttributeError(name)
        return getattr(self._project, name)

    def __getitem__(self, name: str) -> object:
        return getattr(self, name)

    def __iter__(self) -> Iterator[tuple[str, object]]:
        for key in self._CONTEXT_KEYS:
            yield key, getattr(self, key)

    def keys(self) -> tuple[str, ...]:
        return self._CONTEXT_KEYS
