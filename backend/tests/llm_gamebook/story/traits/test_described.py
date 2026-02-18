from llm_gamebook.story.context import StoryContext
from llm_gamebook.story.project import Project
from llm_gamebook.story.template_view import EntityView
from llm_gamebook.story.traits.described import DescribedTrait


def test_described_trait_name_description(simple_project: Project) -> None:
    entity = simple_project.get_entity("node_a", DescribedTrait)

    assert entity.name == "Node A"
    assert entity.description == "First node"


def test_described_trait_enabled_true(
    simple_project: Project, simple_story_context: StoryContext
) -> None:
    entity = simple_project.get_entity("node_a", DescribedTrait)
    view = EntityView(entity, simple_story_context)

    enabled = view.enabled
    assert enabled is True


def test_described_trait_enabled_false(
    simple_project: Project, simple_story_context: StoryContext
) -> None:
    entity = simple_project.get_entity("node_b", DescribedTrait)
    view = EntityView(entity, simple_story_context)

    enabled = view.enabled
    assert enabled is False


def test_described_trait_enabled_expression(
    simple_project: Project, simple_story_context: StoryContext
) -> None:
    entity_c = simple_project.get_entity("node_c", DescribedTrait)
    entity_d = simple_project.get_entity("node_d", DescribedTrait)

    view_c = EntityView(entity_c, simple_story_context)
    view_d = EntityView(entity_d, simple_story_context)

    assert view_c.enabled is True
    assert view_d.enabled is False
