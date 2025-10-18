from collections.abc import Callable, Iterator, Mapping
from typing import TYPE_CHECKING, ClassVar, NamedTuple

from pydantic import BaseModel

from llm_gamebook.schema.validators import is_normalized_snake_case

if TYPE_CHECKING:
    from llm_gamebook.story.entity import BaseEntity

__all__ = ["trait_registry"]


class TraitRegistryEntry(NamedTuple):
    cls: "type[BaseEntity]"
    """Trait type."""

    options_model: type[BaseModel] | None
    """Trait options model."""


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
        self, name: str, options_model: type[BaseModel] | None = None
    ) -> Callable[[type], type]:
        """Class decorator that registers story entity traits."""

        if not is_normalized_snake_case(name):
            msg = f"Trait name must be normalized snake_case {name}"
            raise ValueError(msg)

        def wrapper(cls: type) -> type:
            self._registry[name] = TraitRegistryEntry(cls, options_model)
            return cls

        return wrapper


trait_registry = TraitRegistry()
