from collections.abc import Iterable

from llm_gamebook.story.base import BaseGraph, BaseNode, ToolsMixin
from llm_gamebook.types import StoryTool


class StoryNode(BaseNode):
    def __init__(self, node_id: str, description: str) -> None:
        super().__init__(node_id)
        self.description = description


class Storyline(BaseGraph[StoryNode], ToolsMixin):
    @property
    def tools(self) -> Iterable[StoryTool]:
        return iter(())

    def create_node(self, node_id: str, description: str) -> StoryNode:
        return self._add_node(StoryNode(node_id, description))
