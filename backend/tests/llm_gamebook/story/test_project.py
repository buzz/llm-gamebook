from pathlib import Path

import pytest

from llm_gamebook.schema.project import ProjectDefinition
from llm_gamebook.story.errors import EntityNotFoundError, EntityTypeNotFoundError
from llm_gamebook.story.project import Project


@pytest.fixture
def project_data() -> dict[str, object]:
    return {
        "title": "Test Project",
        "description": "A test project",
        "entity_types": [
            {
                "id": "TestType",
                "name": "Test Type",
                "traits": ["described"],
                "entities": [
                    {
                        "id": "test_entity",
                        "name": "Test Entity",
                        "description": "A test entity",
                    }
                ],
            }
        ],
    }


def test_project_get_template_context(project: Project) -> None:
    context = project.get_template_context()

    assert context["title"] == project.title
    assert context["description"] == project.description
    assert context["author"] == project.author
    assert "entity_types" in context
    assert isinstance(context["entity_types"], list)


def test_project_get_entity_type_found(project: Project) -> None:
    entity_type = project.get_entity_type("StoryArc")

    assert entity_type.id == "StoryArc"
    assert entity_type.name == "Story Arc"


def test_project_get_entity_type_not_found(project: Project) -> None:
    with pytest.raises(EntityTypeNotFoundError) as exc_info:
        project.get_entity_type("NonExistent")

    assert "Entity type not found: NonExistent" in str(exc_info.value)


def test_project_get_entity_found(project: Project) -> None:
    entity = project.get_entity("the_beginning")

    assert entity.id == "the_beginning"


def test_project_get_entity_not_found(project: Project) -> None:
    with pytest.raises(EntityNotFoundError) as exc_info:
        project.get_entity("NonExistent")

    assert "Entity not found: NonExistent" in str(exc_info.value)


def test_project_get_entity_wrong_type(project: Project) -> None:
    entity_type = project.get_entity_type("StoryArc")
    entity = entity_type.get_entity("main")

    with pytest.raises(TypeError):
        project.get_entity("the_beginning", model=type(entity))


def test_project_from_path_not_found() -> None:
    with pytest.raises(FileNotFoundError) as exc_info:
        Project.from_path(Path("/non/existent/path"))

    assert "Project file not found" in str(exc_info.value)


def test_project_from_data(project_data: dict[str, object]) -> None:
    project = Project.from_data(project_data)

    assert project.title == "Test Project"
    assert project.description == "A test project"
    assert "TestType" in project.entity_type_map
    assert "test_entity" in project.entity_type_map["TestType"].entity_map


def test_project_from_definition(project_data: dict[str, object]) -> None:
    project_def = ProjectDefinition.model_validate(project_data, strict=True)
    project = Project.from_definition(project_def)

    assert project.title == "Test Project"
    assert project.description == "A test project"
    assert "TestType" in project.entity_type_map
    assert "test_entity" in project.entity_type_map["TestType"].entity_map


def test_project_entity_type_map_property(simple_project: Project) -> None:
    entity_type_map = simple_project.entity_type_map

    assert isinstance(entity_type_map, dict)
    assert "TestGraph" in entity_type_map
    assert "TestNode" in entity_type_map
    assert len(entity_type_map) == 2
