from collections.abc import Iterable
from typing import TYPE_CHECKING, Any

from llm_gamebook.schema.base import Slug
from llm_gamebook.types import StoryTool

if TYPE_CHECKING:
    from llm_gamebook.story import StoryState


class BaseStoryEntity:
    def __init__(self, slug: Slug, entity_type_slug: Slug, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.slug = slug
        self.entity_type_slug = entity_type_slug
        self._state: StoryState

    def get_tools(self) -> Iterable[StoryTool]:
        """Return instance's tools."""
        return ()

    def register_events(self, state: "StoryState") -> None:
        """Called when story state initialized."""
        self._state = state
