import pytest

from llm_gamebook.story.context import StoryContext
from llm_gamebook.story.schemas import BaseEntity, Project
from llm_gamebook.story.state import SessionStateData
from llm_gamebook.story.template_view import EntityTypeView, EntityView, TemplateContext
from llm_gamebook.story.trait_registry import session_field, trait_registry


@pytest.fixture
def entity(simple_project: Project) -> BaseEntity:
    return simple_project.get_entity("test_graph")


@pytest.fixture
def entity_view(simple_story_context: StoryContext, entity: BaseEntity) -> EntityView:
    return EntityView(entity, simple_story_context)


@pytest.fixture
def entity_type_view(simple_story_context: StoryContext) -> EntityTypeView:
    entity_type = simple_story_context.project.get_entity_type("TestGraph")
    return EntityTypeView(entity_type, simple_story_context)


@pytest.fixture
def template_context(simple_story_context: StoryContext) -> TemplateContext:
    return TemplateContext(simple_story_context)


# Tests for EntityView attribute resolution order


def test_resolver_takes_precedence_over_session_state(
    simple_project: Project, entity: BaseEntity
) -> None:
    session_data = SessionStateData(entities={"test_graph": {"current_node_id": "node_b"}})
    context = StoryContext(simple_project, session_data)
    view = EntityView(entity, context)

    result = view.current_node_id

    assert result == "node_b"


def test_resolver_returns_computed_value(entity_view: EntityView) -> None:
    assert entity_view.current_node_id == "node_a"


def test_session_state_takes_precedence_over_entity_default(
    simple_project: Project, entity: BaseEntity
) -> None:
    session_data = SessionStateData(entities={"test_graph": {"custom_field": 100}})
    context = StoryContext(simple_project, session_data)
    view = EntityView(entity, context)

    result = view.custom_field

    assert result == 100


def test_entity_default_used_when_no_resolver_or_session(entity_view: EntityView) -> None:
    assert entity_view.name == "Test Graph"


def test_missing_attribute_raises_attribute_error(entity_view: EntityView) -> None:
    with pytest.raises(AttributeError):
        _ = entity_view.nonexistent_field


def test_resolver_returns_entity_wrapped(entity_view: EntityView) -> None:
    result = entity_view.current_node

    assert isinstance(result, EntityView)
    assert result._entity.id == "node_a"


def test_entity_view_private_attribute_raises_attribute_error(entity_view: EntityView) -> None:
    with pytest.raises(AttributeError):
        _ = entity_view._private_attr


# Tests for EntityView wrapping of nested entities


def test_nested_baseentity_wrapped(
    simple_story_context: StoryContext, entity_view: EntityView, entity: BaseEntity
) -> None:
    wrapped = entity_view._wrap_if_needed(entity)

    assert isinstance(wrapped, EntityView)
    assert wrapped._entity is entity


def test_list_of_baseentity_wrapped(entity_view: EntityView, entity: BaseEntity) -> None:
    wrapped = entity_view._wrap_if_needed([entity, entity])

    assert isinstance(wrapped, list)
    assert len(wrapped) == 2
    assert all(isinstance(item, EntityView) for item in wrapped)


def test_non_entity_values_not_wrapped(entity_view: EntityView) -> None:
    assert entity_view._wrap_if_needed("string") == "string"
    assert entity_view._wrap_if_needed(42) == 42
    assert entity_view._wrap_if_needed({"key": "value"}) == {"key": "value"}


def test_entity_view_getitem_delegates_to_getattr(entity_view: EntityView) -> None:
    assert entity_view["name"] == entity_view.name


def test_repr_shows_entity_id(entity_view: EntityView) -> None:
    assert repr(entity_view) == "EntityView('test_graph')"


def test_nodes_list_wrapped(entity_view: EntityView) -> None:
    nodes = entity_view.nodes

    assert isinstance(nodes, list)
    assert len(nodes) == 4
    assert all(isinstance(n, EntityView) for n in nodes)


# Tests for TemplateContext project-level field access


def test_title_property(template_context: TemplateContext) -> None:
    assert template_context.title == "Test Project"


def test_description_property(template_context: TemplateContext) -> None:
    assert template_context.description == "A test project"


def test_author_property_none(template_context: TemplateContext) -> None:
    assert template_context.author is None


def test_entity_types_returns_wrapped_list(template_context: TemplateContext) -> None:
    entity_types = template_context.entity_types

    assert isinstance(entity_types, list)
    assert len(entity_types) == 2
    assert all(isinstance(et, EntityTypeView) for et in entity_types)


def test_context_getitem_delegates_to_getattr(template_context: TemplateContext) -> None:
    assert template_context["title"] == template_context.title
    assert template_context["description"] == template_context.description


def test_context_private_attribute_raises_attribute_error(
    template_context: TemplateContext,
) -> None:
    with pytest.raises(AttributeError):
        _ = template_context._private_attr


def test_keys_returns_context_keys(template_context: TemplateContext) -> None:
    assert template_context.keys() == ("title", "description", "author", "entity_types")


def test_iter_yields_key_value_pairs(template_context: TemplateContext) -> None:
    result = dict(template_context)

    assert "title" in result
    assert "description" in result
    assert "author" in result
    assert "entity_types" in result


# Tests for EntityTypeView wrapping


def test_id_property(entity_type_view: EntityTypeView) -> None:
    assert entity_type_view.id == "TestGraph"


def test_name_property(entity_type_view: EntityTypeView) -> None:
    assert entity_type_view.name == "Test Graph"


def test_entities_returns_wrapped_list(simple_story_context: StoryContext) -> None:
    entity_type = simple_story_context.project.get_entity_type("TestNode")
    view = EntityTypeView(entity_type, simple_story_context)
    entities = view.entities

    assert isinstance(entities, list)
    assert len(entities) == 4
    assert all(isinstance(e, EntityView) for e in entities)


def test_traits_property(simple_story_context: StoryContext) -> None:
    entity_type = simple_story_context.project.get_entity_type("TestNode")
    view = EntityTypeView(entity_type, simple_story_context)

    traits = view.traits

    assert isinstance(traits, list)
    assert "described" in traits
    assert "graph_node" in traits


# Tests for @session_field decorator registration


def test_decorator_sets_attribute() -> None:
    class TestClass:
        @session_field("test_field")
        def _resolve_test(self, ctx: StoryContext) -> str:
            return "test"

    method = TestClass._resolve_test
    assert hasattr(method, "_session_field_name")
    assert method._session_field_name == "test_field"


def test_registry_collects_session_fields_for_graph() -> None:
    entry = trait_registry["graph"]

    assert entry.session_fields is not None
    assert "current_node" in entry.session_fields
    assert "current_node_id" in entry.session_fields


def test_registry_collects_session_fields_for_described() -> None:
    entry = trait_registry["described"]

    assert entry.session_fields is not None
    assert "enabled" in entry.session_fields


def test_decorator_preserves_function() -> None:
    class TestClass:
        @session_field("field")
        def _method(self) -> str:
            return "result"

    obj = TestClass()
    assert obj._method() == "result"


def test_multiple_decorators_on_same_class() -> None:
    entry = trait_registry["graph"]

    assert entry.session_fields is not None
    assert len(entry.session_fields) >= 2


# Integration tests verifying templates render correctly with view layer


async def test_get_system_prompt_renders(simple_story_context: StoryContext) -> None:
    result = await simple_story_context.get_system_prompt()

    assert "node_a" in result
    assert "First node" in result
    assert "node_b" not in result


async def test_get_intro_message_renders(simple_story_context: StoryContext) -> None:
    result = await simple_story_context.get_intro_message()

    assert len(result) > 0


async def test_session_state_reflected_in_rendered_output(simple_project: Project) -> None:
    session_data = SessionStateData(entities={"test_graph": {"current_node_id": "node_d"}})
    context = StoryContext(simple_project, session_data)

    result = await context.get_system_prompt()

    assert "node_a" not in result
    assert "node_d" in result
    assert "Fourth node" in result
