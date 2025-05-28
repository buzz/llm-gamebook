import abc
from typing import Any, Self

from llm_gamebook.story.base import BaseStoryEntity


class InvalidTransitionError(Exception):
    pass


class BaseGraphNode(BaseStoryEntity):
    def __init__(
        self,
        name: str,
        description: str | None = None,
        slug: str | None = None,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        super().__init__(name, description, slug, *args, **kwargs)
        self.edges: set[Self] = set()

    def add_edge(self, node: Self) -> None:
        self.edges.add(node)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.slug})"


class BaseGraph[T: BaseGraphNode](BaseStoryEntity, abc.ABC):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.nodes: dict[str, T] = {}
        self._current: T

    @abc.abstractmethod
    def create_node(self, name: str, description: str | None = None, slug: str | None = None) -> T:
        raise NotImplementedError

    @staticmethod
    def add_edge(from_node: T, to_node: T) -> None:
        from_node.add_edge(to_node)

    def transition(self, to_slug: str) -> None:
        try:
            self.current = next(loc for loc in self.current.edges if loc.slug == to_slug)
        except StopIteration as err:
            msg = f"{to_slug} is not a valid transition for this location."
            raise InvalidTransitionError(msg) from err

    @property
    def current(self) -> T:
        return self._current

    @current.setter
    def current(self, new_current: T) -> None:
        self._current = new_current

    def _add_node(self, node: T) -> T:
        if node.slug in self.nodes:
            msg = "Entity is already part of graph"
            raise ValueError(msg)
        self.nodes[node.slug] = node
        return node

    def __repr__(self) -> str:
        return "\n".join(
            f"{node.slug} -> {[n.slug for n in node.edges]}" for node in self.nodes.values()
        )
