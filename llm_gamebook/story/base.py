import abc
from collections.abc import Iterable
from typing import Any, Self

from llm_gamebook.types import StoryTool


class BaseNode:
    def __init__(self, node_id: str) -> None:
        self.id: str = node_id
        self.edges: set[Self] = set()

    def add_edge(self, node: Self) -> None:
        self.edges.add(node)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.id})"


class BaseGraph[T: BaseNode](abc.ABC):
    def __init__(self) -> None:
        self.nodes: dict[str, T] = {}
        self.current: T

    @abc.abstractmethod
    def create_node(self, node_id: str, *args: Any, **kwargs: Any) -> T:
        raise NotImplementedError

    def _add_node(self, node: T) -> T:
        if node.id in self.nodes:
            msg = "Node is already part of graph"
            raise ValueError(msg)
        self.nodes[node.id] = node
        return node

    @staticmethod
    def add_edge(from_node: T, to_node: T) -> None:
        from_node.add_edge(to_node)

    def __repr__(self) -> str:
        return "\n".join(f"{node.id} -> {[n.id for n in node.edges]}" for node in self.nodes.values())


class ToolsMixin(abc.ABC):
    @property
    @abc.abstractmethod
    def tools(self) -> Iterable[StoryTool]:
        raise NotImplementedError
