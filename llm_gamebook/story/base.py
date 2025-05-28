import abc
from collections.abc import Iterable
from typing import Any

from llm_gamebook.types import StoryTool
from llm_gamebook.utils import slugify


class BaseStoryEntity:
    def __init__(
        self,
        name: str,
        description: str | None = None,
        slug: str | None = None,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.name = name
        self.description = description
        self.slug = slug or slugify(name)

    def is_enabled(self) -> bool:
        return True


class EntityConnectionMixin:
    """Mixin for managing connections to related entities."""

    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.entities: list[BaseStoryEntity]

    def add_entity(self, entity: BaseStoryEntity) -> BaseStoryEntity:
        self.entities.append(entity)
        return entity


class ToolsMixin(abc.ABC):
    """Mixin for providing tools to the LLM."""

    @property
    @abc.abstractmethod
    def tools(self) -> Iterable[StoryTool]:
        raise NotImplementedError
