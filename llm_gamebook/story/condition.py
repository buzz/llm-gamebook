import abc
from typing import Any

from llm_gamebook.story.entity import BaseStoryEntity


class BaseCondition(BaseStoryEntity, abc.ABC):
    @abc.abstractmethod
    def is_met(self) -> bool:
        raise NotImplementedError


class IsCurrentLocationCondition(BaseCondition):
    def is_met(self) -> bool:
        return True


class ConditionallyEnabledMixin:
    """Mixin that adds conditions for disabling the entity."""

    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.conditions: list[BaseCondition] = []

    def is_enabled(self) -> bool:
        return all(cond.is_met() for cond in self.conditions)
