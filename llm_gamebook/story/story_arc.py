from typing import Any

from llm_gamebook.story.condition import ConditionallyEnabledMixin
from llm_gamebook.story.graph import BaseGraph, BaseGraphNode


class StoryArcNode(BaseGraphNode):
    def __init__(self, name: str, description: str | None = None, slug: str | None = None) -> None:
        super().__init__(name, description, slug)


class StoryArc(ConditionallyEnabledMixin, BaseGraph[StoryArcNode]):
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
    ) -> StoryArcNode:
        return self._add_node(StoryArcNode(name, description, slug))
