from fastapi import APIRouter, HTTPException

from llm_gamebook.story.errors import ProjectExistsError, ProjectNotFoundError
from llm_gamebook.story.schemas import ProjectSource
from llm_gamebook.story.schemas.project import ProjectDefinition
from llm_gamebook.web.schemas.common import ServerMessage
from llm_gamebook.web.schemas.project import ProjectBasic, ProjectCreate, ProjectDetail, Projects

from .dependencies import ProjectManagerDep

project_router = APIRouter(prefix="/projects", tags=["projects"])


@project_router.get("/")
async def list_projects(
    project_manager: ProjectManagerDep, source: ProjectSource | None = None
) -> Projects:
    projects = [
        ProjectBasic.model_validate(p, from_attributes=True)
        for p in project_manager.list_projects(source)
    ]
    return Projects(data=projects, count=len(projects))


@project_router.get("/{project_id:path}")
async def get_project(project_manager: ProjectManagerDep, project_id: str) -> ProjectDetail:
    try:
        project_def = project_manager.get_project(project_id)
    except ProjectNotFoundError as e:
        raise HTTPException(status_code=404, detail="Project not found") from e

    return ProjectDetail.model_validate(project_def, from_attributes=True)


@project_router.post("/", status_code=201)
async def create_project(
    project_manager: ProjectManagerDep, project_in: ProjectCreate
) -> ProjectBasic:
    try:
        project_def = ProjectDefinition.model_validate(project_in, from_attributes=True)
        project_def = project_manager.create_project(project_def)
    except ProjectExistsError as err:
        raise HTTPException(status_code=409, detail=str(err)) from err
    except ValueError as err:
        raise HTTPException(status_code=400, detail=str(err)) from err

    return ProjectBasic.model_validate(project_def, from_attributes=True)


@project_router.delete("/{project_id:path}")
async def delete_project(project_manager: ProjectManagerDep, project_id: str) -> ServerMessage:
    try:
        project_manager.delete_project(project_id)
    except ProjectNotFoundError as err:
        raise HTTPException(status_code=404, detail="Project not found") from err
    except ValueError as err:
        raise HTTPException(status_code=400, detail=str(err)) from err

    return ServerMessage(message="Project deleted successfully")
