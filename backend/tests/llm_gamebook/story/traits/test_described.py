from llm_gamebook.story.entity import EntityType
from llm_gamebook.story.traits.described import DescribedTrait


def test_described_trait_get_template_context(simple_entity_type: EntityType) -> None:
    """Test DescribedTrait.get_template_context includes name and description."""
    entity = simple_entity_type.entity_map["node_a"]

    assert isinstance(entity, DescribedTrait)

    context = entity.get_template_context()

    assert "name" in context
    assert "description" in context
    assert "enabled" in context
    assert context["name"] == "Node A"
    assert context["description"] == "First node"


def test_described_trait_enabled_true(simple_entity_type: EntityType) -> None:
    """Test DescribedTrait with enabled=True evaluates correctly."""
    entity = simple_entity_type.entity_map["node_a"]

    context = entity.get_template_context()

    assert context["enabled"] is True


def test_described_trait_enabled_false(simple_entity_type: EntityType) -> None:
    """Test DescribedTrait with enabled=False evaluates correctly."""
    entity = simple_entity_type.entity_map["node_b"]

    context = entity.get_template_context()

    assert context["enabled"] is False


def test_described_trait_enabled_expression(simple_entity_type: EntityType) -> None:
    """Test DescribedTrait with BoolExprDefinition enabled expression."""
    entity_c = simple_entity_type.entity_map["node_c"]
    entity_d = simple_entity_type.entity_map["node_d"]

    context_c = entity_c.get_template_context()
    context_d = entity_d.get_template_context()

    assert context_c["enabled"] is True
    assert context_d["enabled"] is False
