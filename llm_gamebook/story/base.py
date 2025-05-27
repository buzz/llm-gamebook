import abc
from collections.abc import Iterable
from typing import Any

from openai.types.chat import ChatCompletionToolParam


class BaseNode:
    def __init__(self, node_id: str) -> None:
        self.id: str = node_id
        self.edges: list[BaseNode] = []

    def add_edge(self, node: "BaseNode") -> None:
        self.edges.append(node)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.id})"


class BaseGraph[T: BaseNode](abc.ABC):
    def __init__(self) -> None:
        self.nodes: dict[str, T] = {}
        self.current: T

    def add_node(self, node_id: str, *args: Any, **kwargs: Any) -> T:
        if node_id not in self.nodes:
            self.nodes[node_id] = self._create_node(node_id, *args, **kwargs)
        return self.nodes[node_id]

    @staticmethod
    def add_edge(from_node: T, to_node: T) -> None:
        from_node.add_edge(to_node)

    @staticmethod
    @abc.abstractmethod
    def _create_node(node_id: str, *args: Any, **kwargs: Any) -> T:
        raise NotImplementedError

    def __repr__(self) -> str:
        return "\n".join(f"{node.id} -> {[n.id for n in node.edges]}" for node in self.nodes.values())


class LlmFunctionMixin(abc.ABC):
    @property
    @abc.abstractmethod
    def function_params(self) -> Iterable[ChatCompletionToolParam]:
        raise NotImplementedError
