from collections.abc import Iterable, Mapping
from typing import TYPE_CHECKING

from pydantic import BaseModel, Field, PrivateAttr
from pydantic_ai import RunContext, Tool
from pydantic_ai.tools import ToolDefinition

from llm_gamebook.story.entity import BaseEntity
from llm_gamebook.story.trait_registry import trait_registry
from llm_gamebook.story.types import (
    FunctionResult,
    NormalizedPascalCase,
    NormalizedSnakeCase,
    StoryTool,
)

if TYPE_CHECKING:
    from llm_gamebook.schema.entity import FunctionDefinition
    from llm_gamebook.story.state import StoryState


class InvalidTransitionError(Exception):
    pass


@trait_registry.register("graph_node")
class GraphNodeTrait(BaseEntity):
    """Adds the capability to be used as graph node to an entity."""

    edge_ids: list[NormalizedSnakeCase] = Field(default=[])
    """List of edge IDs."""

    _edges: "list[GraphNodeTrait]" = PrivateAttr()
    """List of resolved edge entities."""

    @property
    def edges(self) -> "list[GraphNodeTrait]":
        return self._edges

    def get_template_context(self) -> Mapping[str, object]:
        return {
            **super().get_template_context(),
            "edges": [node.id for node in self._edges],
        }

    def post_init(self) -> None:
        self._resolve_edge_ids()

    def _resolve_edge_ids(self) -> None:
        """Resolve edge IDs to actual entities."""
        self._edges = [
            self.entity_type.get_entity(entity_id, GraphNodeTrait) for entity_id in self.edge_ids
        ]


class GraphTraitOptions(BaseModel):
    node_type_id: NormalizedPascalCase
    """The ID of the graph node entity type."""


@trait_registry.register("graph", GraphTraitOptions)
class GraphTrait(BaseEntity):
    """Adds the capability to be used as graph to an entity."""

    node_ids: list[NormalizedSnakeCase]
    """List of entity IDs that are part of the graph."""

    _nodes: list[GraphNodeTrait]
    """List of resolved entities that are part of the graph."""

    _current_node: GraphNodeTrait
    """The current graph node."""

    @property
    def current_node_id(self) -> NormalizedSnakeCase:
        """ID of current graph node."""
        return self._current_node.id

    @property
    def nodes(self) -> list[GraphNodeTrait]:
        return self._nodes

    @property
    def current_node(self) -> GraphNodeTrait:
        return self._current_node

    def get_template_context(self) -> Mapping[str, object]:
        return {
            **super().get_template_context(),
            "nodes": [node.get_template_context() for node in self._nodes],
            "current_node": self.current_node.get_template_context(),
        }

    def get_tools(self) -> Iterable[StoryTool]:
        yield from super().get_tools()

        for func_spec in self.entity_type.functions or ():
            if func_spec.target == "transition":
                yield self._make_transition_tool(func_spec)

    def post_init(self) -> None:
        self._resolve_node_ids()

    def _make_transition_tool(self, func_spec: "FunctionDefinition") -> StoryTool:
        def transition(to: str) -> FunctionResult:
            """Transition to another graph node.

            Args:
                to: The node to transition to.
            """
            try:
                self.transition(to)
            except InvalidTransitionError as err:
                return {"result": "error", "reason": str(err)}

            return {"result": "success"}

        async def prepare(
            ctx: "RunContext[StoryState]", tool_def: ToolDefinition
        ) -> ToolDefinition | None:
            schema = tool_def.parameters_json_schema
            edge_ids = [edge.id for edge in self.current_node.edges]

            # Don't expose transition function if there are no nodes to transition to
            if len(edge_ids) == 0:
                return None

            # Provide LLM with a list of valid IDs
            schema["properties"]["to"]["enum"] = edge_ids

            if func_spec.properties:
                self._update_schema_descriptions(schema, func_spec.properties)

            return tool_def

        return Tool(
            transition,
            name=func_spec.name,
            description=func_spec.description,
            strict=True,
            require_parameter_descriptions=True,
            prepare=prepare,
        )

    def transition(self, to: str) -> None:
        try:
            self._current_node = next(node for node in self._current_node.edges if node.id == to)
        except StopIteration as err:
            msg = f"{to} is not a valid transition for node {self._current_node.id}"
            raise InvalidTransitionError(msg) from err

    def _resolve_node_ids(self) -> None:
        """Resolve node IDs to actual entities."""
        # Get node entity type
        options = self.entity_type.get_trait_options("graph", GraphTraitOptions)
        node_type = self.project.get_entity_type(options.node_type_id)

        # Nodes
        self._nodes = [
            node_type.get_entity(entity_id, GraphNodeTrait) for entity_id in self.node_ids
        ]

        # Current node
        try:
            self._current_node = next(
                node for node in self._nodes if node.id == self.current_node_id
            )
        except StopIteration as err:
            msg = f"Graph {self.id}: current_node {self.current_node_id} not found"
            raise ValueError(msg) from err
