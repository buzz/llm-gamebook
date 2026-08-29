"""Execution of core game actions (end-game, reset-game, restore, fork).

Core actions that only transform the in-memory state use the store's
reducers. Actions with database side effects (end-game, restore, fork) are
coordinated here.
"""

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING, cast
from uuid import UUID

from pydantic import BaseModel
from sqlmodel.ext.asyncio.session import AsyncSession as AsyncDbSession

from llm_gamebook.db.crud.message import find_previous_state, get_message_count
from llm_gamebook.db.crud.session import (
    create_fork_session,
    get_session,
    mark_session_ended,
    reset_session,
    update_session_state,
)
from llm_gamebook.db.models import Session
from llm_gamebook.story.errors import CoreActionError, InvalidStepError, NoStateError
from llm_gamebook.story.state import (
    Action,
    EndGamePayload,
    ResetGameAction,
    SessionState,
    SessionStateData,
    StepPayload,
)

if TYPE_CHECKING:
    from llm_gamebook.story import StoryContext

logger = logging.getLogger(__name__)

CORE_END_GAME = "core/end-game"
CORE_RESET_GAME = "core/reset-game"
CORE_RESTORE = "core/restore"
CORE_FORK = "core/fork"


@dataclass(frozen=True)
class CoreActionResult:
    """Result of executing a core action."""

    new_session_id: UUID | None = None
    """ID of the new session created by a fork action, if any."""


class CoreActionExecutor:
    """Executes core game actions for a session."""

    def __init__(self, session_id: UUID, context: "StoryContext") -> None:
        self._session_id = session_id
        self._context = context

    async def execute[T: BaseModel](
        self, db_session: AsyncDbSession, action: Action[T]
    ) -> CoreActionResult:
        """Execute a core action and return its result."""
        processed_action = cast("Action[BaseModel]", action)
        if action.name == CORE_END_GAME:
            return await self._end_game(db_session, processed_action)
        if action.name == CORE_RESET_GAME:
            return await self._reset_game(db_session)
        if action.name == CORE_RESTORE:
            return await self._restore(db_session, processed_action)
        if action.name == CORE_FORK:
            return await self._fork(db_session, processed_action)

        msg = f"Unknown core action: {action.name}"
        raise CoreActionError(msg)

    async def _get_session_or_raise(self, db_session: AsyncDbSession) -> Session:
        session = await get_session(db_session, self._session_id)
        if session is None:
            msg = f"Session {self._session_id} not found"
            raise CoreActionError(msg)
        return session

    async def _end_game(
        self, db_session: AsyncDbSession, action: Action[BaseModel]
    ) -> CoreActionResult:
        payload = EndGamePayload.model_validate(action.payload.model_dump())
        session = await self._get_session_or_raise(db_session)
        if session.ended_at is not None:
            logger.info("Session %s already ended, ignoring end-game action", self._session_id)
            return CoreActionResult()

        await mark_session_ended(db_session, self._session_id)
        logger.info("Session %s ended (reason: %s)", self._session_id, payload.reason)
        return CoreActionResult()

    async def _reset_game(self, db_session: AsyncDbSession) -> CoreActionResult:
        await self._get_session_or_raise(db_session)

        # Clear in-memory state via the registered reducer (idempotent)
        self._context.store.dispatch(ResetGameAction())
        await reset_session(db_session, self._session_id)
        logger.info("Session %s reset to project defaults", self._session_id)
        return CoreActionResult()

    async def _restore(
        self, db_session: AsyncDbSession, action: Action[BaseModel]
    ) -> CoreActionResult:
        payload = StepPayload.model_validate(action.payload.model_dump())
        await self._validate_step(db_session, payload.step)

        snapshot = await find_previous_state(db_session, self._session_id, payload.step)
        if snapshot is not None:
            state = SessionState(
                SessionStateData.model_validate(snapshot),
                read_only_fields=self._context.read_only_fields,
            )
        else:
            # No state at or before the target step: restore to the start
            state = SessionState(read_only_fields=self._context.read_only_fields)
        self._context.store.set_state(state)
        await update_session_state(db_session, self._session_id, snapshot)
        logger.info("Session %s restored to step %s", self._session_id, payload.step)
        return CoreActionResult()

    async def _fork(
        self, db_session: AsyncDbSession, action: Action[BaseModel]
    ) -> CoreActionResult:
        payload = StepPayload.model_validate(action.payload.model_dump())
        await self._validate_step(db_session, payload.step)

        snapshot = await find_previous_state(db_session, self._session_id, payload.step)
        if snapshot is None:
            msg = f"No state found at or before step {payload.step} to fork from"
            raise NoStateError(msg)

        source = await self._get_session_or_raise(db_session)
        fork = await create_fork_session(db_session, source, snapshot)
        logger.info(
            "Forked session %s into new session %s at step %s",
            self._session_id,
            fork.id,
            payload.step,
        )
        return CoreActionResult(new_session_id=fork.id)

    async def _validate_step(self, db_session: AsyncDbSession, step: int) -> None:
        if step < -1:
            msg = f"Invalid step number: {step} (expected -1 for latest or a 0-based index)"
            raise InvalidStepError(msg)

        latest = await get_message_count(db_session, self._session_id) - 1
        if step > latest:
            msg = f"Step {step} is greater than the current step {latest}"
            raise InvalidStepError(msg)
