from collections.abc import Iterable
from typing import TYPE_CHECKING, Any

from pydantic_ai.tools import ObjectJsonSchema

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

    @staticmethod
    def _update_schema_descriptions(schema: ObjectJsonSchema, descriptions: dict[str, str]) -> None:
        """Update tool definition with custom property descriptions."""
        for key, descr in descriptions.items():
            try:
                schema["properties"][key]["description"] = descr
            except KeyError as err:
                msg = f"Property {key} not in argument for function {{trans_func.name}}"
                raise ValueError(msg) from err
