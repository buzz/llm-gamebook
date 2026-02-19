from pydantic_ai import RunContext, RunUsage
from pydantic_ai.models.test import TestModel

from llm_gamebook.story.context import StoryContext
from llm_gamebook.story.schemas import EntityType, Project
from llm_gamebook.story.state import Action
from llm_gamebook.story.template_view import EntityView
from llm_gamebook.story.traits.graph import (
    GraphNodeTrait,
    GraphTrait,
    GraphTransitionAction,
    GraphTransitionPayload,
)


def test_graph_node_trait_edges_property(simple_entity_type: EntityType) -> None:
    entity = simple_entity_type.get_entity("node_a", GraphNodeTrait)
    assert len(entity.edges) == 1
    assert entity.edges[0].id == "node_b"


def test_graph_node_trait_post_init(simple_entity_type: EntityType) -> None:
    entity = simple_entity_type.get_entity("node_a", GraphNodeTrait)
    assert hasattr(entity, "_edges")
    assert isinstance(entity._edges, list)


def test_graph_node_trait_resolve_edge_ids(simple_entity_type: EntityType) -> None:
    entity = simple_entity_type.get_entity("node_a", GraphNodeTrait)
    assert len(entity._edges) == 1
    assert entity._edges[0].id == "node_b"


def test_graph_node_trait_view_edges(
    simple_project: Project, simple_story_context: StoryContext
) -> None:
    entity = simple_project.get_entity("node_a", GraphNodeTrait)
    view = EntityView(entity, simple_story_context)
    edges = view.edges
    assert isinstance(edges, list)
    assert len(edges) == 1
    assert edges[0].id == "node_b"


def test_graph_trait_nodes_property(simple_project: Project) -> None:
    graph_entity = simple_project.get_entity("test_graph", GraphTrait)
    nodes = graph_entity.nodes
    assert len(nodes) == 4
    assert nodes[0].id == "node_a"
    assert nodes[1].id == "node_b"
    assert nodes[2].id == "node_c"
    assert nodes[3].id == "node_d"


def test_graph_trait_current_node_property(simple_project: Project) -> None:
    graph_entity = simple_project.get_entity("test_graph", GraphTrait)
    current_node = graph_entity.current_node
    assert current_node.id == "node_a"


def test_graph_trait_transition_valid(
    simple_project: Project, simple_story_context: StoryContext
) -> None:
    graph_entity = simple_project.get_entity("test_graph", GraphTrait)

    action = GraphTransitionAction(entity_id="test_graph", to="node_b")
    simple_story_context.store.dispatch(action)

    effective_node_id = graph_entity._resolve_current_node_id(simple_story_context)
    assert effective_node_id == "node_b"


def test_graph_trait_transition_invalid(
    simple_project: Project, simple_story_context: StoryContext
) -> None:
    graph_entity = simple_project.get_entity("test_graph", GraphTrait)

    current_node = graph_entity._resolve_current_node(simple_story_context)
    valid_targets = [edge.id for edge in current_node.edges]

    assert "node_z" not in valid_targets


def test_graph_trait_resolve_node_ids(simple_project: Project) -> None:
    graph_entity = simple_project.get_entity("test_graph", GraphTrait)
    assert len(graph_entity._nodes) == 4
    assert graph_entity._current_node.id == "node_a"


def test_graph_trait_get_tools(simple_project: Project) -> None:
    graph_entity = simple_project.get_entity("test_graph", GraphTrait)
    tools = list(graph_entity.get_tools())
    assert len(tools) == 1


def test_graph_trait_make_transition_tool(simple_project: Project) -> None:
    graph_entity = simple_project.get_entity("test_graph", GraphTrait)
    assert graph_entity.functions is not None
    func_spec = graph_entity.functions[0]
    tool = graph_entity._make_transition_tool(func_spec)
    assert tool.name == "transition"


def test_graph_trait_prepare_function(simple_project: Project) -> None:
    graph_entity = simple_project.get_entity("test_graph", GraphTrait)
    assert graph_entity.functions is not None
    func_spec = graph_entity.functions[0]
    tool = graph_entity._make_transition_tool(func_spec)

    result = tool.prepare
    assert result is not None


def test_graph_trait_prepare_function_no_edges(simple_project: Project) -> None:
    node_b = simple_project.get_entity("node_b", GraphNodeTrait)
    assert len(node_b.edge_ids) == 0


def test_create_graph_transition_action() -> None:
    action = GraphTransitionAction(entity_id="graph_1", to="start_node")
    assert action.name == "graph/transition"
    assert action.payload.entity_id == "graph_1"
    assert action.payload.to == "start_node"


def test_graph_transition_serialization() -> None:
    action = GraphTransitionAction(entity_id="graph_1", to="node1")
    json_str = action.model_dump_json()
    assert "graph/transition" in json_str
    assert "node1" in json_str


def test_graph_transition_roundtrip() -> None:
    original = GraphTransitionAction(entity_id="graph_1", to="next_node")
    json_str = original.model_dump_json()
    restored = Action[GraphTransitionPayload].model_validate_json(json_str)
    assert restored.name == original.name
    assert restored.payload.entity_id == original.payload.entity_id
    assert restored.payload.to == original.payload.to


def test_transition_tool_dispatches_action(
    simple_project: Project, simple_story_context: StoryContext
) -> None:
    graph_entity = simple_project.get_entity("test_graph", GraphTrait)
    assert graph_entity.functions is not None
    func_spec = graph_entity.functions[0]
    tool = graph_entity._make_transition_tool(func_spec)

    ctx = RunContext(
        deps=simple_story_context,
        model=TestModel(),
        usage=RunUsage(),
        messages=[],
    )

    result = tool.function(ctx, to="node_b")

    assert result == {"result": "success"}
    assert simple_story_context.session_state.get_field("test_graph", "current_node_id") == "node_b"


def test_transition_tool_validates_target(
    simple_project: Project, simple_story_context: StoryContext
) -> None:
    graph_entity = simple_project.get_entity("test_graph", GraphTrait)
    assert graph_entity.functions is not None
    func_spec = graph_entity.functions[0]
    tool = graph_entity._make_transition_tool(func_spec)

    ctx = RunContext(
        deps=simple_story_context,
        model=TestModel(),
        usage=RunUsage(),
        messages=[],
    )

    result = tool.function(ctx, to="invalid_node")

    assert result["result"] == "error"
    assert "invalid_node" in result.get("reason", "")


def test_multiple_transitions_accumulate_state(
    simple_project: Project, simple_story_context: StoryContext
) -> None:
    action1 = GraphTransitionAction(entity_id="test_graph", to="node_b")
    simple_story_context.store.dispatch(action1)
    assert simple_story_context.session_state.get_field("test_graph", "current_node_id") == "node_b"

    action2 = GraphTransitionAction(entity_id="test_graph", to="node_a")
    simple_story_context.store.dispatch(action2)
    assert simple_story_context.session_state.get_field("test_graph", "current_node_id") == "node_a"
