import abc
from typing import Any

from llm_gamebook.story.base import BaseStoryEntity
from llm_gamebook.story.location import Location, Locations


class BaseCondition(BaseStoryEntity, abc.ABC):
    @abc.abstractmethod
    def is_met(self) -> bool:
        raise NotImplementedError


class IsCurrentLocationCondition(BaseCondition):
    def __init__(
        self,
        name: str,
        location: Location,
        locations: Locations,
        description: str | None = None,
        slug: str | None = None,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        super().__init__(name, description, slug, *args, **kwargs)
        self.location = location
        self.locations = locations

    def is_met(self) -> bool:
        return self.locations.current.slug == self.location.slug


class ConditionallyEnabledMixin:
    """Mixin that adds conditions for disabling the entity."""

    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.conditions: list[BaseCondition] = []

    def is_enabled(self) -> bool:
        return all(cond.is_met() for cond in self.conditions)
