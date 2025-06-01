from collections.abc import Iterable, Mapping, Sequence
from typing import TYPE_CHECKING, Any

from pydantic_ai.tools import ObjectJsonSchema

if TYPE_CHECKING:
    from llm_gamebook.story import StoryState
    from llm_gamebook.types import StoryTool


type EntityProperty = Sequence[BaseStoryEntity] | BaseStoryEntity | str | bool | int | float


class BaseStoryEntity:
    def __init__(
        self,
        id_: str,
        entity_type_id: str,
        *args: Any,
        **kwargs: Any,
    ):
        super().__init__(*args, **kwargs)
        self.id = id_
        self.entity_type_id = entity_type_id
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
