from collections.abc import Iterable

from llm_gamebook.story.base import BaseGraph, BaseNode


class StoryNode(BaseNode):
    def __init__(self, node_id: str, description: Iterable[str]) -> None:
        super().__init__(node_id)
        self.description = description


class Storyline(BaseGraph[StoryNode]):
    @staticmethod
    def _create_node(node_id: str, description: Iterable[str]) -> StoryNode:
        return StoryNode(node_id, description)
