from collections.abc import Callable, Iterator, Mapping
from typing import TYPE_CHECKING, ClassVar, NamedTuple, ParamSpec, TypeVar

from pydantic import BaseModel

from llm_gamebook.schema.validators import is_normalized_snake_case

if TYPE_CHECKING:
    from .entity import BaseEntity
    from .store import Reducer

__all__ = ["reducer", "session_field", "trait_registry"]

_SESSION_FIELD_ATTR = "_session_field_name"
_REDUCER_ATTR = "_reducer_action_name"

P = ParamSpec("P")
R = TypeVar("R")


def session_field(field_name: str) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """Decorator to mark a method as a session field resolver."""

    def decorator(method: Callable[P, R]) -> Callable[P, R]:
        setattr(method, _SESSION_FIELD_ATTR, field_name)
        return method

    return decorator


def reducer(action_name: str) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """Decorator to mark a method as a reducer."""

    def decorator(method: Callable[P, R]) -> Callable[P, R]:
        setattr(method, _REDUCER_ATTR, action_name)
        return method

    return decorator


class TraitRegistryEntry(NamedTuple):
    cls: "type[BaseEntity]"
    """Trait type."""

    options_model: type[BaseModel] | None
    """Trait options model."""

    reducers: Mapping[str, "Reducer"] | None
    """Reducers mapping action names to reducer functions."""

    session_fields: Mapping[str, str] | None
    """Session fields mapping field names to resolver method names."""


class TraitRegistry(Mapping[str, TraitRegistryEntry]):
    """Central registry singleton class that maps IDs to traits."""

    _registry: ClassVar[dict[str, TraitRegistryEntry]] = {}

    def __getitem__(self, key: str) -> TraitRegistryEntry:
        return self._registry[key]

    def __iter__(self) -> Iterator[str]:
        return iter(self._registry)

    def __len__(self) -> int:
        return len(self._registry)

    def register(
        self,
        name: str,
        options_model: type[BaseModel] | None = None,
        reducers: Mapping[str, "Reducer"] | None = None,
    ) -> Callable[[type], type]:
        """Class decorator that registers story entity traits."""

        if not is_normalized_snake_case(name):
            msg = f"Trait name must be normalized snake_case {name}"
            raise ValueError(msg)

        def wrapper(cls: type) -> type:
            session_fields: dict[str, str] = {}
            for attr_name in dir(cls):
                method = getattr(cls, attr_name, None)
                if method is None:
                    continue
                field_name = getattr(method, _SESSION_FIELD_ATTR, None)
                if field_name is not None:
                    session_fields[field_name] = attr_name

            self._registry[name] = TraitRegistryEntry(
                cls,
                options_model,
                reducers,
                session_fields or None,
            )
            return cls

        return wrapper

    def get_all_reducers(self) -> dict[str, list["Reducer"]]:
        """Get all registered reducers grouped by action name."""
        result: dict[str, list[Reducer]] = {}
        for entry in self._registry.values():
            if entry.reducers:
                for action_name, reducer in entry.reducers.items():
                    if action_name not in result:
                        result[action_name] = []
                    result[action_name].append(reducer)
        return result


trait_registry = TraitRegistry()
