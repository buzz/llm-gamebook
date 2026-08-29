from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from sqlmodel.ext.asyncio.session import AsyncSession as AsyncDbSession

from llm_gamebook.db.crud.message import get_message_count, get_state_snapshots
from llm_gamebook.db.crud.model_config import get_model_config
from llm_gamebook.db.crud.session import create_session as crud_create_session
from llm_gamebook.db.crud.session import (
    get_session,
    get_session_count,
    get_sessions,
    update_session_model_config,
)
from llm_gamebook.db.models import Message
from llm_gamebook.db.models import Session as SqlModelSession
from llm_gamebook.engine.core_actions import CoreActionResult
from llm_gamebook.engine.engine import StoryEngine
from llm_gamebook.engine.message import SessionModelConfigChangedMessage
from llm_gamebook.story.errors import CoreActionError, InvalidStepError, ProjectNotFoundError
from llm_gamebook.story.state import (
    Action,
    EndGameAction,
    ForkAction,
    ResetGameAction,
    RestoreAction,
)
from llm_gamebook.web.schemas.common import ServerMessage
from llm_gamebook.web.schemas.session import (
    EndGameRequest,
    Session,
    SessionCreate,
    SessionFull,
    Sessions,
    SessionUpdate,
    StateEntry,
    StateHistory,
    StepRequest,
)
from llm_gamebook.web.schemas.session.message import ModelRequest, ModelRequestCreate

from ._tags import ApiTags
from .dependencies import DbSessionDep, MessageBusDep, ProjectManagerDep, StoryEngineDep

session_router = APIRouter(prefix="/sessions", tags=[ApiTags.sessions])


def _core_action_http_error(error: CoreActionError) -> HTTPException:
    """Map a core-action error to the corresponding HTTP error.

    Invalid steps are client errors (422); missing state snapshots and
    generic core-action failures are resource state conflicts (409).
    Missing sessions already surface as 404 via the engine dependency.

    Args:
        error: The core-action error raised by the engine.

    Returns:
        The HTTP exception to raise for the given core-action error.
    """
    if isinstance(error, InvalidStepError):
        return HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(error))
    return HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(error))


async def _run_core_action[T: BaseModel](
    engine: StoryEngine, db_session: AsyncDbSession, action: Action[T]
) -> CoreActionResult:
    """Execute a core action, mapping its errors to HTTP exceptions."""
    try:
        return await engine.execute_core_action(db_session, action)
    except CoreActionError as error:
        raise _core_action_http_error(error) from error


async def _validate_step_bound(db_session: AsyncDbSession, session_id: UUID, step: int) -> None:
    """Raise 422 if the step is beyond the session's message range.

    The lower bound (step >= -1) is enforced by the StepRequest schema.

    Args:
        db_session: The async database session.
        session_id: The session the step targets.
        step: The target step (0-based message index, -1 for latest).

    Raises:
        HTTPException: 422 if the step is greater than the latest message index.
    """
    latest = await get_message_count(db_session, session_id) - 1
    if step > latest:
        detail = f"Step {step} is greater than the current step {latest}"
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=detail)


@session_router.get("/")
async def read_sessions(
    db_session: DbSessionDep, project_id: str | None = None, skip: int = 0, limit: int = 100
) -> Sessions:
    sessions = await get_sessions(db_session, project_id, skip, limit)

    return Sessions(
        data=[Session.model_validate(s, from_attributes=True) for s in sessions],
        count=await get_session_count(db_session, project_id),
    )


@session_router.get("/{session_id}", response_model=SessionFull)
async def read_session(engine: StoryEngineDep, db_session: DbSessionDep) -> SqlModelSession:
    session = await engine.session_adapter.get_session(db_session)

    if not session:
        # If we get this far, the session must be available
        raise HTTPException(status_code=500, detail="Story session expected")

    return session


@session_router.post("/", status_code=status.HTTP_201_CREATED)
async def create_session(
    db_session: DbSessionDep, project_manager: ProjectManagerDep, session_in: SessionCreate
) -> Session:
    model_config = await get_model_config(db_session, session_in.config_id)
    if not model_config:
        raise HTTPException(status_code=404, detail="Model config not found")

    try:
        project = project_manager.get_project(session_in.project_id)
    except ProjectNotFoundError as err:
        raise HTTPException(status_code=404, detail="Project not found") from err

    session = await crud_create_session(db_session, model_config, project.id, session_in.title)

    return Session.model_validate({**session.model_dump(), "message_count": 0})


@session_router.patch("/{session_id}")
async def update_session(
    db_session: DbSessionDep,
    session_id: str,
    session_update: SessionUpdate,
    message_bus: MessageBusDep,
) -> ServerMessage:
    session_uuid = UUID(session_id)
    await update_session_model_config(db_session, session_uuid, session_update.config_id)

    if session_update.config_id:
        config = await get_model_config(db_session, session_update.config_id)
        if config:
            message_bus.publish(
                SessionModelConfigChangedMessage(
                    session_id=session_uuid,
                    model_name=config.model_name,
                    provider=config.provider,
                    base_url=config.base_url,
                    api_key=config.api_key,
                ),
            )

    return ServerMessage(message="Session updated successfully.")


@session_router.post(
    "/{session_id}/request", response_model=ModelRequest, status_code=status.HTTP_201_CREATED
)
async def create_model_request(
    engine: StoryEngineDep, db_session: DbSessionDep, message_in: ModelRequestCreate
) -> Message:
    return await engine.session_adapter.create_user_request(db_session, message_in.content)


@session_router.post("/{session_id}/restore")
async def restore_state(
    engine: StoryEngineDep, db_session: DbSessionDep, session_id: UUID, request: StepRequest
) -> ServerMessage:
    await _validate_step_bound(db_session, session_id, request.step)
    await _run_core_action(engine, db_session, RestoreAction(step=request.step))

    return ServerMessage(message="Session state restored.")


@session_router.post(
    "/{session_id}/fork", response_model=SessionFull, status_code=status.HTTP_201_CREATED
)
async def fork_state(
    engine: StoryEngineDep, db_session: DbSessionDep, session_id: UUID, request: StepRequest
) -> SqlModelSession:
    await _validate_step_bound(db_session, session_id, request.step)
    result = await _run_core_action(engine, db_session, ForkAction(step=request.step))

    new_session_id = result.new_session_id
    if new_session_id is None:
        raise HTTPException(status_code=500, detail="Fork did not produce a new session")

    forked = await get_session(db_session, new_session_id)
    if forked is None:
        raise HTTPException(status_code=500, detail="Forked session not found")

    return forked


@session_router.post("/{session_id}/end-game")
async def end_game(
    engine: StoryEngineDep, db_session: DbSessionDep, body: EndGameRequest | None = None
) -> ServerMessage:
    reason = body.reason if body else None
    await _run_core_action(engine, db_session, EndGameAction(reason=reason))

    return ServerMessage(message="Game ended.")


@session_router.post("/{session_id}/reset")
async def reset_session(engine: StoryEngineDep, db_session: DbSessionDep) -> ServerMessage:
    await _run_core_action(engine, db_session, ResetGameAction())

    return ServerMessage(message="Session reset to project defaults.")


@session_router.get("/{session_id}/states", response_model=StateHistory)
async def get_states(db_session: DbSessionDep, session_id: UUID) -> StateHistory:
    if await get_session(db_session, session_id) is None:
        raise HTTPException(status_code=404, detail="Session not found")

    snapshots = await get_state_snapshots(db_session, session_id)
    return StateHistory(
        data=[
            StateEntry(step=s.step, timestamp=s.created_at, field_count=s.field_count)
            for s in snapshots
        ]
    )


@session_router.delete("/{session_id}")
async def delete_session(engine: StoryEngineDep, db_session: DbSessionDep) -> ServerMessage:
    await engine.session_adapter.delete_session(db_session)
    return ServerMessage(message="Story session deleted successfully.")
