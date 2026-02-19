from collections.abc import Callable, Iterator, Mapping
from typing import TYPE_CHECKING, ClassVar, Final, NamedTuple, ParamSpec, TypeVar

from pydantic import BaseModel

from llm_gamebook.story.errors import TraitNotFoundError

from .schemas.validators import is_normalized_snake_case

if TYPE_CHECKING:
    from .schemas import BaseEntity
    from .state import Reducer

__all__ = ["reducer", "session_field", "trait_registry"]

_SESSION_FIELD_ATTR: Final = "_session_field_name"
_REDUCER_ATTR: Final = "_reducer_action_name"

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
    cls: type["BaseEntity"]
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

    def get_by_type(self, cls: type["BaseEntity"]) -> TraitRegistryEntry:
        try:
            return next(e for e in self.values() if e.cls == cls)
        except StopIteration as e:
            raise TraitNotFoundError from e

    def register(
        self, name: str, options_model: type[BaseModel] | None = None
    ) -> Callable[[type], type]:
        """Class decorator that registers story entity traits."""

        if not is_normalized_snake_case(name):
            msg = f"Trait name must be normalized snake_case {name}"
            raise ValueError(msg)

        def wrapper(cls: type) -> type:
            session_fields: dict[str, str] = {}
            reducers: dict[str, Reducer] = {}

            # Collect session fields & reducers
            for attr_name in dir(cls):
                method = getattr(cls, attr_name, None)
                if not callable(method):
                    continue

                # session field?
                try:
                    method_name = getattr(method, _SESSION_FIELD_ATTR)
                except AttributeError:
                    pass
                else:
                    if isinstance(method_name, str):
                        session_fields[method_name] = attr_name

                # reducer method?
                try:
                    action_name = getattr(method, _REDUCER_ATTR)
                except AttributeError:
                    pass
                else:
                    if isinstance(action_name, str):
                        # Check if it's a staticmethod
                        raw_attr = cls.__dict__.get(attr_name)
                        if not isinstance(raw_attr, staticmethod):
                            msg = f"Reducer '{cls.__name__}::{attr_name}' is not a staticmethod"
                            raise TypeError(msg)

                        reducers[action_name] = getattr(cls, attr_name)

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
