from typing import cast

import pytest

from llm_gamebook.story.entity import BaseEntity, EntityType
from llm_gamebook.story.errors import EntityNotFoundError, TraitNotFoundError
from llm_gamebook.story.project import Project
from llm_gamebook.story.traits.graph import GraphNodeTrait, GraphTrait, GraphTraitOptions


def test_base_entity_get_template_context(simple_entity_type: EntityType) -> None:
    """Test BaseEntity.get_template_context returns correct context."""
    entity = simple_entity_type.entity_map["node_a"]

    context = entity.get_template_context()

    assert context["id"] == "node_a"
    assert context["entity_type_id"] == simple_entity_type.id


def test_base_entity_get_tools(simple_entity_type: EntityType) -> None:
    """Test BaseEntity.get_tools returns tools from entities."""
    entity = simple_entity_type.entity_map["node_a"]

    tools = list(entity.get_tools())

    assert tools == []


def test_base_entity_post_init(simple_entity_type: EntityType) -> None:
    """Test BaseEntity.post_init does nothing (no-op) for non-trait entities."""
    entity = simple_entity_type.entity_map["node_a"]

    entity.post_init()


def test_base_entity_from_definition(simple_entity_type: EntityType) -> None:
    """Test BaseEntity.from_definition creates entity from definition."""
    entity_def = simple_entity_type.entity_map["node_a"]
    project = entity_def.project
    entity_cls = type(entity_def)

    entity = BaseEntity.from_definition(
        entity_def=entity_def,
        entity_type=simple_entity_type,
        entity_cls=entity_cls,
        project=project,
    )

    assert entity.id == "node_a"
    assert entity.entity_type is simple_entity_type
    assert entity.project is project


def test_entity_type_get_entity_found(simple_entity_type: EntityType) -> None:
    """Test EntityType.get_entity returns entity when found."""
    entity = simple_entity_type.get_entity("node_a")

    assert entity is not None
    assert entity.id == "node_a"


def test_entity_type_get_entity_not_found(simple_entity_type: EntityType) -> None:
    """Test EntityType.get_entity raises EntityNotFoundError when not found."""
    with pytest.raises(EntityNotFoundError):
        simple_entity_type.get_entity("nonexistent")


def test_entity_type_get_entity_wrong_type(simple_entity_type: EntityType) -> None:
    """Test EntityType.get_entity raises TypeError when entity has wrong type."""
    with pytest.raises(TypeError):
        simple_entity_type.get_entity("node_a", GraphTrait)


def test_entity_type_get_trait_options_found(simple_project: Project) -> None:
    """Test EntityType.get_trait_options returns options when trait has options."""
    graph_entity_type = simple_project.get_entity_type("TestGraph")

    options = graph_entity_type.get_trait_options("graph", GraphTraitOptions)

    assert options is not None
    assert options.node_type_id == "TestNode"


def test_entity_type_get_trait_options_not_found(simple_project: Project) -> None:
    """Test EntityType.get_trait_options raises TraitNotFoundError when not found."""
    graph_entity_type = simple_project.get_entity_type("TestGraph")

    with pytest.raises(TraitNotFoundError):
        graph_entity_type.get_trait_options("nonexistent", GraphTraitOptions)


def test_entity_type_get_trait_options_wrong_type(simple_project: Project) -> None:
    """Test EntityType.get_trait_options raises TypeError when options have wrong type."""
    graph_entity_type = simple_project.get_entity_type("TestGraph")

    with pytest.raises(TypeError):
        graph_entity_type.get_trait_options("graph", GraphNodeTrait)


def test_entity_type_get_template_context(simple_entity_type: EntityType) -> None:
    """Test EntityType.get_template_context returns correct context."""
    context = simple_entity_type.get_template_context()

    assert context["id"] == "TestNode"
    assert context["name"] == "Test Node"
    assert "traits" in context
    assert "entities" in context
    entities_list: list[dict[str, object]] = cast("list[dict[str, object]]", context["entities"])
    assert len(entities_list) == 2


def test_entity_type_get_tools(simple_entity_type: EntityType) -> None:
    """Test EntityType.get_tools returns tools from all entities."""
    tools = list(simple_entity_type.get_tools())

    assert tools == []


def test_entity_type_post_init(simple_entity_type: EntityType) -> None:
    """Test EntityType.post_init calls post_init on all entities."""
    for entity in simple_entity_type.entity_map.values():
        entity.post_init()


def test_entity_type_type_from_definition(simple_project: Project) -> None:
    """Test EntityType._type_from_definition creates correct entity class."""
    entity_type_def = simple_project.entity_type_map["TestGraph"]

    entity_cls, trait_options = EntityType._type_from_definition(
        entity_type_def, type(simple_project)
    )

    assert entity_cls is not None
    assert "graph" in trait_options


def test_entity_type_from_definition(simple_project: Project) -> None:
    """Test EntityType.from_definition creates entity type from definition."""
    entity_type_def = simple_project.entity_type_map["TestNode"]

    entity_type = EntityType.from_definition(entity_type_def, simple_project)

    assert entity_type.id == "TestNode"
    assert len(entity_type.entity_map) == 2
    assert "node_a" in entity_type.entity_map
    assert "node_b" in entity_type.entity_map
