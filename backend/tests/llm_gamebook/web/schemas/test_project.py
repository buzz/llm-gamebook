from llm_gamebook.story.schemas import ProjectSource
from llm_gamebook.story.schemas.entity import EntityTypeDefinition
from llm_gamebook.story.schemas.project import ProjectDefinition
from llm_gamebook.web.schemas.project import ProjectBasic, ProjectCreate, ProjectDetail, Projects


def test_project_basic_model() -> None:
    project = ProjectBasic(
        id="namespace/name",
        source=ProjectSource.LOCAL,
        title="Test Project",
        author="Test Author",
        description="A test project",
    )
    assert project.id == "namespace/name"
    assert project.source == ProjectSource.LOCAL
    assert project.title == "Test Project"
    assert project.author == "Test Author"
    assert project.description == "A test project"


def test_project_basic_from_project_definition() -> None:
    project_def = ProjectDefinition(
        id="namespace/name",
        source=ProjectSource.EXAMPLE,
        title="Test Project",
        author="Test Author",
        description="A test project",
    )
    project = ProjectBasic.model_validate(project_def, from_attributes=True)
    assert project.id == "namespace/name"
    assert project.source == ProjectSource.EXAMPLE
    assert project.title == "Test Project"
    assert project.author == "Test Author"
    assert project.description == "A test project"


def test_project_detail_model() -> None:
    entity_type = EntityTypeDefinition(
        id="Character",
        name="Character",
        entities=[],
    )
    project = ProjectDetail(
        id="namespace/name",
        source=ProjectSource.LOCAL,
        title="Test Project",
        entity_types=[entity_type],
    )
    assert project.id == "namespace/name"
    assert project.source == ProjectSource.LOCAL
    assert project.title == "Test Project"
    assert len(project.entity_types) == 1
    assert project.entity_types[0].id == "Character"


def test_project_detail_from_project_definition() -> None:
    entity_type = EntityTypeDefinition(
        id="Location",
        name="Location",
        entities=[],
    )
    project_def = ProjectDefinition(
        id="namespace/name",
        source=ProjectSource.LOCAL,
        title="Test Project",
        description="A test project",
        entity_types=[entity_type],
    )
    project = ProjectDetail.model_validate(project_def, from_attributes=True)
    assert project.id == "namespace/name"
    assert project.source == ProjectSource.LOCAL
    assert project.title == "Test Project"
    assert project.description == "A test project"
    assert len(project.entity_types) == 1
    assert project.entity_types[0].id == "Location"


def test_project_create_model() -> None:
    project = ProjectCreate(
        id="namespace/name",
        source=ProjectSource.LOCAL,
        title="Test Project",
        author="Test Author",
    )
    assert project.id == "namespace/name"
    assert project.source == ProjectSource.LOCAL
    assert project.title == "Test Project"
    assert project.author == "Test Author"
    assert project.description is None


def test_projects_model() -> None:
    project1 = ProjectBasic(
        id="namespace/project-one",
        source=ProjectSource.LOCAL,
        title="Project 1",
    )
    project2 = ProjectBasic(
        id="namespace/project-two",
        source=ProjectSource.EXAMPLE,
        title="Project 2",
    )
    projects = Projects(data=[project1, project2], count=2)
    assert len(projects.data) == 2
    assert projects.count == 2
    assert projects.data[0].id == "namespace/project-one"
    assert projects.data[1].id == "namespace/project-two"


def test_projects_with_empty_list() -> None:
    projects = Projects(data=[], count=0)
    assert projects.data == []
    assert projects.count == 0
