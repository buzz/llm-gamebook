from collections.abc import Iterable, Mapping
from typing import TYPE_CHECKING, Any

from pydantic import BaseModel
from pydantic_ai import RunContext, Tool
from pydantic_ai.tools import ToolDefinition

from llm_gamebook.story.entity import BaseStoryEntity
from llm_gamebook.story.traits.registry import trait
from llm_gamebook.types import FunctionResult, NormalizedPascalCase, NormalizedSnakeCase, StoryTool

if TYPE_CHECKING:
    from llm_gamebook.engine.context import StoryContext
    from llm_gamebook.schema.entity import FunctionSpec
    from llm_gamebook.story.state import StoryState


class InvalidTransitionError(Exception):
    pass


@trait("graph_node")
class GraphNodeTrait(BaseStoryEntity):
    """Adds the capability to be used as graph node to an entity."""

    def __init__(self, edges: list[NormalizedSnakeCase] | None = None, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.edges: list[GraphNodeTrait]

        # Remember ids for resolving them later
        self._edge_ids = edges or []

    def resolve_edge_ids(self, node_entity_id: str) -> None:
        """Resolve edge ids to actual entities."""
        self.edges = [
            self._state.get_entity(id_, node_entity_id, GraphNodeTrait) for id_ in self._edge_ids
        ]


class GraphTraitParams(BaseModel):
    node_entity: NormalizedPascalCase
    """The graph node entity type."""


@trait("graph", GraphTraitParams)
class GraphTrait(BaseStoryEntity):
    """Adds the capability to be used as graph to an entity."""

    def __init__(
        self,
        nodes: list[NormalizedSnakeCase],
        current_node: NormalizedSnakeCase,
        *args: Any,
        **kwargs: Any,
    ):
        super().__init__(*args, **kwargs)
        self.nodes: list[GraphNodeTrait]
        self.current_node: GraphNodeTrait

        # Remember ids for resolving them later
        self.node_ids = nodes
        self.current_node_id = current_node

    def get_template_context(
        self, entities: "Mapping[str, BaseStoryEntity]"
    ) -> Mapping[str, object]:
        ctx = super().get_template_context(entities)
        return {
            **ctx,
            "nodes": [node.get_template_context(entities) for node in self.nodes],
            "current_node": self.current_node.get_template_context(entities),
        }

    def get_tools(self) -> Iterable[StoryTool]:
        yield from super().get_tools()

        entity_type = self._state.get_entity_type(self.entity_type_id)
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
            self.current_node = next(node for node in self.current_node.edges if node.id == to)
        except StopIteration as err:
            msg = f"{to} is not a valid transition for node {self.current_node.id}"
            raise InvalidTransitionError(msg) from err

    def register_events(self, state: "StoryState") -> None:
        super().register_events(state)
        state.subscribe("init", self._resolve_node_ids)

    def _resolve_node_ids(self) -> None:
        """Resolve node IDs to actual entities."""
        # Get node entity ID
        params = self._state.get_trait_params(self.entity_type_id, "graph", GraphTraitParams)
        node_entity_id = params.node_entity

        # Nodes
        self.nodes = [
            self._state.get_entity(id_, node_entity_id, GraphNodeTrait) for id_ in self.node_ids
        ]

        # Current node
        try:
            self.current_node = next(node for node in self.nodes if node.id == self.current_node_id)
        except StopIteration as err:
            msg = f"Graph {self.id}: current_node {self.current_node_id} not found"
            raise ValueError(msg) from err

        # Resolve edge IDs for each node
        for node in self.nodes:
            node.resolve_edge_ids(node_entity_id)
