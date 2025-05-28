from collections.abc import Iterable
from typing import TYPE_CHECKING, Any

from pydantic_ai.tools import Tool, ToolDefinition

from llm_gamebook.story.base import EntityConnectionMixin, ToolsMixin
from llm_gamebook.story.graph import BaseGraph, BaseGraphNode, InvalidTransitionError
from llm_gamebook.types import FunctionResult, StoryTool

if TYPE_CHECKING:
    from pydantic_ai import RunContext

    from llm_gamebook.story.context import StoryContext


class Location(BaseGraphNode, EntityConnectionMixin):
    def __init__(self, name: str, description: str | None = None, slug: str | None = None) -> None:
        super().__init__(name, description, slug)
        self.is_visited = False


class Locations(BaseGraph[Location], ToolsMixin):
    def __init__(
        self,
        name: str,
        description: str | None = None,
        slug: str | None = None,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        super().__init__(name, description, slug, *args, **kwargs)

    def create_node(
        self,
        name: str,
        description: str | None = None,
        slug: str | None = None,
    ) -> Location:
        return self._add_node(Location(name, description, slug))

    @property
    def current(self) -> Location:
        return super().current

    @current.setter
    def current(self, new_current: Location) -> None:
        self.current = new_current
        self.current.is_visited = True

    @property
    def tools(self) -> Iterable[StoryTool]:
        if len(self.current.edges) > 0:
            yield Tool(
                self._change_location,
                name="change_location",
                strict=True,
                require_parameter_descriptions=True,
                prepare=self._prepare_change_location,
            )

    def _change_location(self, location_slug: str) -> FunctionResult:
        """Player moves to another location.

        Args:
            location_slug: The location to move to.
        """
        try:
            self.transition(location_slug)
        except InvalidTransitionError as err:
            return {"result": "error", "reason": str(err)}
        return {"result": "success"}

    async def _prepare_change_location(
        self,
        ctx: "RunContext[StoryContext]",
        tool_def: ToolDefinition,
    ) -> ToolDefinition | None:
        if len(ctx.messages) <= 1:
            # No changing location on introductory message
            return None

        # Specify exact IDs that are valid
        tool_def.parameters_json_schema["properties"]["location_slug"]["enum"] = [
            edge.slug for edge in self.current.edges
        ]
        return tool_def
