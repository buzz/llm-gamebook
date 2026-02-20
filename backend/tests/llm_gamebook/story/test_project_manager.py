from pathlib import Path

import pytest

from llm_gamebook.constants import PROJECT_FILENAME
from llm_gamebook.story import ProjectManager
from llm_gamebook.story.errors import ProjectExistsError, ProjectNotFoundError
from llm_gamebook.story.schemas.project import ProjectDefinition, ProjectSource


def test_project_manager_init_default() -> None:
    manager = ProjectManager()

    assert manager._local_projects_path is not None


def test_project_manager_init_custom_path(tmp_path: Path) -> None:
    manager = ProjectManager(local_projects_path=tmp_path)

    assert manager._local_projects_path == tmp_path


def test_project_manager_list_projects_all(project_manager: ProjectManager) -> None:
    projects = list(project_manager.list_projects())

    assert len(projects) >= 1
    project_ids = [p.id for p in projects]
    assert "llm-gamebook/broken-bulb" in project_ids


def test_project_manager_list_projects_example_only(project_manager: ProjectManager) -> None:
    projects = list(project_manager.list_projects(source=ProjectSource.EXAMPLE))

    assert len(projects) >= 1
    for project in projects:
        assert project.source == ProjectSource.EXAMPLE


def test_project_manager_list_projects_local_only(project_manager: ProjectManager) -> None:
    projects = list(project_manager.list_projects(source=ProjectSource.LOCAL))

    for project in projects:
        assert project.source == ProjectSource.LOCAL


def test_project_manager_get_project_found(project_manager: ProjectManager) -> None:
    project = project_manager.get_project("llm-gamebook/broken-bulb")

    assert project.id == "llm-gamebook/broken-bulb"
    assert project.title == "Broken Bulb"
    assert project.source == ProjectSource.EXAMPLE


def test_project_manager_get_project_not_found(project_manager: ProjectManager) -> None:
    with pytest.raises(ProjectNotFoundError):
        project_manager.get_project("nonexistent/project")


def test_project_manager_create_project(project_manager: ProjectManager) -> None:
    project_def = ProjectDefinition(
        id="test-namespace/test-project",
        source=ProjectSource.LOCAL,
        title="Test Project",
        description="A test project",
    )

    created = project_manager.create_project(project_def)

    assert created.id == "test-namespace/test-project"
    project_path = project_manager._local_projects_path / "test-namespace" / "test-project"
    assert project_path.exists()
    assert (project_path / PROJECT_FILENAME).exists()


def test_project_manager_create_project_already_exists(project_manager: ProjectManager) -> None:
    project_def = ProjectDefinition(
        id="test-namespace/test-project",
        source=ProjectSource.LOCAL,
        title="Test Project",
        description="A test project",
    )
    project_manager.create_project(project_def)

    with pytest.raises(ProjectExistsError):
        project_manager.create_project(project_def)


def test_project_manager_delete_project(project_manager: ProjectManager) -> None:
    project_def = ProjectDefinition(
        id="test-namespace/test-project",
        source=ProjectSource.LOCAL,
        title="Test Project",
        description="A test project",
    )
    project_manager.create_project(project_def)

    project_manager.delete_project("test-namespace/test-project")

    project_path = project_manager._local_projects_path / "test-namespace" / "test-project"
    assert not project_path.exists()


def test_project_manager_delete_project_not_local(project_manager: ProjectManager) -> None:
    with pytest.raises(ValueError, match="Can only delete local projects"):
        project_manager.delete_project("llm-gamebook/broken-bulb")


def test_project_manager_delete_project_not_found(project_manager: ProjectManager) -> None:
    with pytest.raises(ProjectNotFoundError):
        project_manager.delete_project("nonexistent/project")


def test_project_manager_discover_from_directory(tmp_path: Path) -> None:
    namespace_dir = tmp_path / "test-namespace"
    project_dir = namespace_dir / "test-project"
    project_dir.mkdir(parents=True)
    (project_dir / PROJECT_FILENAME).write_text("title: Test\ndescription: A test\n")

    projects = list(ProjectManager._discover_from_directory(tmp_path, ProjectSource.LOCAL))

    assert len(projects) == 1
    assert projects[0].id == "test-namespace/test-project"
    assert projects[0].source == ProjectSource.LOCAL


def test_project_manager_iterdir(tmp_path: Path) -> None:
    valid_dir = tmp_path / "valid-name"
    valid_dir.mkdir()
    invalid_dir = tmp_path / "InvalidName"
    invalid_dir.mkdir()
    file_path = tmp_path / "file.txt"
    file_path.touch()

    dirs = list(ProjectManager._iterdir(tmp_path))

    assert len(dirs) == 1
    assert dirs[0].name == "valid-name"
