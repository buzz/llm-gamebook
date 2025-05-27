from collections.abc import Iterable
from typing import TYPE_CHECKING

from pydantic_ai.tools import Tool, ToolDefinition

from llm_gamebook.story.base import BaseGraph, BaseNode, ToolsMixin
from llm_gamebook.types import FunctionResult, StoryTool

if TYPE_CHECKING:
    from pydantic_ai import RunContext

    from llm_gamebook.story.context import StoryContext


class Location(BaseNode):
    def __init__(self, node_id: str, description: str) -> None:
        super().__init__(node_id)
        self.description = description


class Locations(BaseGraph[Location], ToolsMixin):
    def create_node(self, node_id: str, description: str) -> Location:
        return self._add_node(Location(node_id, description))

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

    def _change_location(self, location_id: str) -> FunctionResult:
        """Player moves to another location.

        Args:
            location_id: The location to move to.
        """
        try:
            self.current = next(loc for loc in self.current.edges if loc.id == location_id)
        except StopIteration:
            return {"result": "error", "reason": f"{location_id} is not a valid transition for this location."}
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
        tool_def.parameters_json_schema["properties"]["location_id"]["enum"] = [edge.id for edge in self.current.edges]
        return tool_def
