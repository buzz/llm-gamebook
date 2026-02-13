import pytest

from llm_gamebook.story.entity import EntityType
from llm_gamebook.story.project import Project
from llm_gamebook.story.traits.graph import GraphNodeTrait, GraphTrait, InvalidTransitionError


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


def test_graph_node_trait_get_template_context(simple_entity_type: EntityType) -> None:
    entity = simple_entity_type.get_entity("node_a", GraphNodeTrait)
    context = entity.get_template_context()
    assert context["id"] == "node_a"
    assert context["edges"] == ["node_b"]


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


def test_graph_trait_transition_valid(simple_project: Project) -> None:
    graph_entity = simple_project.get_entity("test_graph", GraphTrait)
    graph_entity.transition("node_b")
    assert graph_entity.current_node.id == "node_b"


def test_graph_trait_transition_invalid(simple_project: Project) -> None:
    graph_entity = simple_project.get_entity("test_graph", GraphTrait)
    with pytest.raises(InvalidTransitionError):
        graph_entity.transition("node_z")


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
