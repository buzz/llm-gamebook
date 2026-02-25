from fastapi import APIRouter, HTTPException, Response

from llm_gamebook.story.errors import ProjectExistsError, ProjectNotFoundError
from llm_gamebook.story.schemas import ProjectSource
from llm_gamebook.story.schemas.project import ProjectDefinition
from llm_gamebook.story.types import NormalizedKebabCase
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


@project_router.get("/{project_namespace}/{project_name}")
async def get_project(
    project_manager: ProjectManagerDep,
    project_namespace: NormalizedKebabCase,
    project_name: NormalizedKebabCase,
) -> ProjectDetail:
    project_id = f"{project_namespace}/{project_name}"

    try:
        project_def = project_manager.get_project(project_id)
    except ProjectNotFoundError as e:
        raise HTTPException(status_code=404, detail="Project not found") from e

    return ProjectDetail.model_validate(project_def, from_attributes=True)


@project_router.get("/{project_namespace}/{project_name}/image")
async def get_project_image(
    project_manager: ProjectManagerDep,
    project_namespace: NormalizedKebabCase,
    project_name: NormalizedKebabCase,
) -> Response:
    project_id = f"{project_namespace}/{project_name}"

    try:
        image_path = project_manager.get_image_path(project_id)
    except ProjectNotFoundError as e:
        raise HTTPException(status_code=404, detail="Project not found") from e

    if image_path is None:
        raise HTTPException(status_code=404, detail="Project has no image")

    try:
        image_bytes = image_path.read_bytes()
    except OSError as e:
        raise HTTPException(status_code=404, detail="Could not read project image") from e

    # TODO: media-type
    return Response(image_bytes)


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


@project_router.delete("/{project_namespace}/{project_name}")
async def delete_project(
    project_manager: ProjectManagerDep,
    project_namespace: NormalizedKebabCase,
    project_name: NormalizedKebabCase,
) -> ServerMessage:
    project_id = f"{project_namespace}/{project_name}"

    try:
        project_manager.delete_project(project_id)
    except ProjectNotFoundError as err:
        raise HTTPException(status_code=404, detail="Project not found") from err
    except ValueError as err:
        raise HTTPException(status_code=400, detail=str(err)) from err

    return ServerMessage(message="Project deleted successfully")
