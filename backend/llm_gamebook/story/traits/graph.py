from collections.abc import Iterable
from contextlib import suppress
from typing import TYPE_CHECKING

from pydantic import BaseModel, Field, PrivateAttr, ValidationError
from pydantic_ai import RunContext, Tool
from pydantic_ai.tools import ToolDefinition

from llm_gamebook.story.context import StoryContext
from llm_gamebook.story.errors import EntityFieldNotFoundError
from llm_gamebook.story.schemas import BaseEntity
from llm_gamebook.story.state import Action, SessionState
from llm_gamebook.story.trait_registry import reducer, session_field, trait_registry
from llm_gamebook.story.types import (
    FunctionResult,
    NormalizedPascalCase,
    NormalizedSnakeCase,
    StoryTool,
)

if TYPE_CHECKING:
    from llm_gamebook.schemas.entity import FunctionDefinition


class InvalidTransitionError(Exception):
    pass


class GraphTransitionPayload(BaseModel):
    """Payload for GraphTransitionAction."""

    entity_id: str
    to: str


class GraphTransitionAction(Action[GraphTransitionPayload]):
    """Action for transitioning an entity to a new graph node."""

    def __init__(self, entity_id: str, to: str) -> None:
        super().__init__(
            name="graph/transition", payload=GraphTransitionPayload(entity_id=entity_id, to=to)
        )


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
    """The current graph node (project default)."""

    @property
    def current_node_id(self) -> NormalizedSnakeCase:
        """ID of current graph node (project default)."""
        return self._current_node.id

    @property
    def nodes(self) -> list[GraphNodeTrait]:
        return self._nodes

    @property
    def current_node(self) -> GraphNodeTrait:
        """Current graph node (project default)."""
        return self._current_node

    @session_field("current_node_id")
    def _resolve_current_node_id(self, story_context: StoryContext) -> str | None:
        """Get effective current_node_id from session state or project default."""
        with suppress(EntityFieldNotFoundError):
            effective = story_context.get_field(self.id, "current_node_id")
            return str(effective)
        return self.current_node_id

    @session_field("current_node")
    def _resolve_current_node(self, story_context: StoryContext) -> GraphNodeTrait:
        """Get current node based on session state override or project default."""
        node_id = self._resolve_current_node_id(story_context)
        if node_id is None:
            return self._current_node
        return next((n for n in self._nodes if n.id == node_id), self._current_node)

    @staticmethod
    @reducer("graph/transition")
    def graph_transition_reducer(state: SessionState, action: Action[BaseModel]) -> SessionState:
        """Reducer for graph/transition action."""
        payload = GraphTransitionPayload.model_validate(action.payload.model_dump())
        state.set_field(payload.entity_id, "current_node_id", payload.to)
        return state

    def get_tools(self) -> Iterable[StoryTool]:
        yield from super().get_tools()

        for func_spec in self.functions or ():
            if func_spec.target == "transition":
                yield self._make_transition_tool(func_spec)

    def post_init(self) -> None:
        self._resolve_node_ids()

    def _make_transition_tool(self, func_spec: "FunctionDefinition") -> StoryTool:
        entity_id = self.id

        def transition(ctx: RunContext[StoryContext], to: str) -> FunctionResult:
            """Transition to another graph node.

            Args:
                to: The node to transition to.
            """
            story_ctx = ctx.deps

            if not story_ctx.validate_entity_exists(entity_id):
                return {"result": "error", "reason": f"Entity '{entity_id}' not found in project"}

            if to not in self.node_ids:
                return {
                    "result": "error",
                    "reason": f"Node '{to}' is not part of graph '{entity_id}'",
                }

            current_node = self._resolve_current_node(story_ctx)

            valid_targets = [edge.id for edge in current_node.edges]
            if to not in valid_targets:
                return {
                    "result": "error",
                    "reason": f"{to} is not a valid transition from {current_node.id}",
                }

            action = GraphTransitionAction(entity_id, to)
            try:
                story_ctx.store.dispatch(action)
            except (RuntimeError, TypeError, ValidationError) as err:
                return {"result": "error", "reason": str(err)}
            else:
                return {"result": "success"}

        async def prepare(
            ctx: RunContext[StoryContext], tool_def: ToolDefinition
        ) -> ToolDefinition | None:
            story_ctx = ctx.deps
            current_node = self._resolve_current_node(story_ctx)
            edge_ids = [edge.id for edge in current_node.edges]

            if len(edge_ids) == 0:
                return None

            schema = tool_def.parameters_json_schema
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
        initial_node_id = (self.__pydantic_extra__ or {}).get("current_node_id")
        if initial_node_id:
            self._current_node = next(
                (n for n in self._nodes if n.id == initial_node_id), self._nodes[0]
            )
        else:
            self._current_node = self._nodes[0]
