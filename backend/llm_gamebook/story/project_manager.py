import shutil
from collections.abc import Iterator
from contextlib import suppress
from pathlib import Path

from llm_gamebook.constants import EXAMPLES_PATH, PROJECTS_PATH
from llm_gamebook.story.errors import ProjectNotFoundError
from llm_gamebook.utils import normalized_kebab_case

from .schemas.project import ProjectDefinition, ProjectSource


class ProjectManager:
    """Manage directory-based story projects."""

    def __init__(self, local_projects_path: Path | None = None) -> None:
        self._local_projects_path = local_projects_path or PROJECTS_PATH

    def list_projects(self, source: ProjectSource | None = None) -> Iterator[ProjectDefinition]:
        if source is None or source == ProjectSource.EXAMPLE:
            yield from self._discover_from_directory(EXAMPLES_PATH, ProjectSource.EXAMPLE)
        if source is None or source == ProjectSource.LOCAL:
            yield from self._discover_from_directory(self._local_projects_path, ProjectSource.LOCAL)

    def get_project(self, project_id: str) -> ProjectDefinition:
        projects = self.list_projects()
        with suppress(StopIteration):
            return next(p for p in projects if p.id == project_id)
        raise ProjectNotFoundError

    def create_project(self, project_def: ProjectDefinition) -> ProjectDefinition:
        project_path = self._local_projects_path / project_def.namespace / project_def.name
        project_def.save(project_path)
        return project_def

    def delete_project(self, project_id: str) -> None:
        project = self.get_project(project_id)
        if project.source != ProjectSource.LOCAL:
            msg = "Can only delete local projects"
            raise ValueError(msg)
        shutil.rmtree(self._local_projects_path / project.namespace / project.name)

    @classmethod
    def _discover_from_directory(
        cls, base_dir: Path, source: ProjectSource
    ) -> Iterator[ProjectDefinition]:
        for namespace_dir in cls._iterdir(base_dir):
            for project_dir in cls._iterdir(namespace_dir):
                proj_def = ProjectDefinition.from_path(project_dir)
                proj_def.source = source
                yield proj_def

    @staticmethod
    def _iterdir(path: Path) -> Iterator[Path]:
        yield from (
            p for p in path.iterdir() if p.is_dir() and p.name == normalized_kebab_case(p.name)
        )
