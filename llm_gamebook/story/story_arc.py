from collections.abc import Mapping

from llm_gamebook.story.base import BaseGraph, BaseNode


class StoryArcNode(BaseNode):
    def __init__(self, node_id: str, description: str) -> None:
        super().__init__(node_id)
        self.description = description


class StoryArc(BaseGraph[StoryArcNode]):
    def __init__(self, name: str):
        super().__init__()
        self.name = name

    def create_node(self, node_id: str, description: str) -> StoryArcNode:
        return self._add_node(StoryArcNode(node_id, description))

    def get_template_context(self) -> Mapping[str, object]:
        return {
            "name": self.name,
            "current": self.current,
        }
