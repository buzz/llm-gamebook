from collections.abc import Iterable
from typing import TYPE_CHECKING, Any

from pydantic import BaseModel
from pydantic_ai import RunContext, Tool
from pydantic_ai.tools import ToolDefinition

from llm_gamebook.schema.base import Slug
from llm_gamebook.story.entity import BaseStoryEntity
from llm_gamebook.story.traits.registry import trait
from llm_gamebook.types import FunctionResult, StoryTool

if TYPE_CHECKING:
    from llm_gamebook.engine.context import StoryContext
    from llm_gamebook.schema.entity import FunctionSpec
    from llm_gamebook.story.state import StoryState


class InvalidTransitionError(Exception):
    pass


@trait("graph-node")
class GraphNodeTrait(BaseStoryEntity):
    """Adds the capability to be used as graph node to an entity."""

    def __init__(self, edges: list[Slug] | None = None, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.edges: list[GraphNodeTrait]

        # Remember slugs for resolving them later
        self._edge_slugs = edges or []

    def resolve_edge_slugs(self, node_entity_slug: Slug) -> None:
        """Resolve edge slugs to actual instances."""
        self.edges = [
            self._state.get_instance(slug, node_entity_slug, GraphNodeTrait)
            for slug in self._edge_slugs
        ]


class GraphTraitParams(BaseModel):
    node_entity: Slug
    """The graph node entity type."""


@trait("graph", GraphTraitParams)
class GraphTrait(BaseStoryEntity):
    """Adds the capability to be used as graph to an entity."""

    def __init__(self, nodes: list[Slug], current_node: Slug, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.nodes: list[GraphNodeTrait]
        self.current_node: GraphNodeTrait

        # Remember slugs for resolving them later
        self._node_slugs = nodes
        self._current_node_slug = current_node

    def get_tools(self) -> Iterable[StoryTool]:
        """Return instance's tools."""
        yield from super().get_tools()

        entity_type = self._state.get_entity_type(self.entity_type_slug)
        for func_spec in entity_type.functions or ():
            if func_spec.target == "transition":
                yield self._make_transition_tool(func_spec)

    def _make_transition_tool(self, func_spec: "FunctionSpec") -> StoryTool:
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
            ctx: "RunContext[StoryContext]", tool_def: ToolDefinition
        ) -> ToolDefinition | None:
            schema = tool_def.parameters_json_schema
            edge_slugs = [edge.slug for edge in self.current_node.edges]

            # Don't expose transition function if there are no nodes to transition to
            if len(edge_slugs) == 0:
                return None

            # Provide LLM with a list of valid slugs
            schema["properties"]["to"]["enum"] = edge_slugs

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
            self.current_node = next(node for node in self.current_node.edges if node.slug == to)
        except StopIteration as err:
            msg = f"{to} is not a valid transition for node {self.current_node.slug}"
            raise InvalidTransitionError(msg) from err

    def register_events(self, state: "StoryState") -> None:
        super().register_events(state)
        state.subscribe("init", self._resolve_node_slugs)

    def _resolve_node_slugs(self) -> None:
        """Resolve node slugs to actual instances."""
        # Get node entity slug
        params = self._state.get_trait_params(self.entity_type_slug, "graph", GraphTraitParams)
        node_entity_slug = params.node_entity

        # Nodes
        self.nodes = [
            self._state.get_instance(slug, node_entity_slug, GraphNodeTrait)
            for slug in self._node_slugs
        ]

        # Current node
        try:
            self.current_node = next(
                node for node in self.nodes if node.slug == self._current_node_slug
            )
        except StopIteration as err:
            msg = f"Graph {self.slug}: current_node {self._current_node_slug} not found"
            raise ValueError(msg) from err

        # Resolve edge slugs for each node
        for node in self.nodes:
            node.resolve_edge_slugs(node_entity_slug)
