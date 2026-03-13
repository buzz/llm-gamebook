import asyncio
import time
from contextlib import suppress
from types import TracebackType
from typing import Self
from uuid import UUID

from pydantic import ValidationError
from pydantic_ai.models import Model
from sqlalchemy.orm import selectinload
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession as AsyncDbSession

from llm_gamebook.db.crud.message import get_latest_message_with_state
from llm_gamebook.db.models import Session
from llm_gamebook.logger import logger
from llm_gamebook.message_bus import BusSubscriber, MessageBus
from llm_gamebook.providers import ModelProvider
from llm_gamebook.story.context import StoryContext
from llm_gamebook.story.project_manager import ProjectManager
from llm_gamebook.story.schemas.project import Project
from llm_gamebook.story.state import SessionStateData

from ._model_factory import create_model_from_db_config
from .engine import StoryEngine
from .message import EngineCreated, SessionDeleted, SessionModelConfigChangedMessage


class EngineManager(BusSubscriber):
    def __init__(self, bus: MessageBus, max_idle_seconds: int = 600) -> None:
        self._log = logger.getChild("engine-manager")

        self._bus = bus
        self._engines: dict[UUID, tuple[StoryEngine, float]] = {}  # engine, last_used
        self._max_idle = max_idle_seconds
        self._evict_task = asyncio.create_task(self._evict_idle())

        self._subscribe(SessionDeleted, self._on_session_deleted)
        self._subscribe(SessionModelConfigChangedMessage, self._on_model_config_changed)

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        if self._evict_task and not self._evict_task.done():
            self._evict_task.cancel()
            with suppress(asyncio.CancelledError):
                await self._evict_task

    def get(self, session_id: UUID) -> StoryEngine:
        engine, _ = self._engines[session_id]
        self._engines[session_id] = (engine, time.time())  # bump last used
        return engine

    async def get_or_create(
        self,
        session_id: UUID,
        db_session: AsyncDbSession,
        project_manager: ProjectManager,
    ) -> StoryEngine:
        created: bool = False
        try:
            engine, _ = self._engines[session_id]
        except KeyError:
            result = await self._create_model_and_context(session_id, db_session, project_manager)
            model, context = result
            engine = StoryEngine(session_id, model, context, self._bus)
            created = True

        self._engines[session_id] = (engine, time.time())

        if created:
            self._bus.publish(EngineCreated(session_id))

        return engine

    async def _create_model_and_context(
        self,
        session_id: UUID,
        db_session: AsyncDbSession,
        project_manager: ProjectManager,
    ) -> tuple[Model | None, StoryContext]:
        stmt = select(Session).where(Session.id == session_id)
        stmt = stmt.options(selectinload(Session.config))
        result = await db_session.exec(stmt)
        session = result.one_or_none()

        if not session:
            msg = f"Session {session_id} not found"
            raise ValueError(msg)

        message_with_state = await get_latest_message_with_state(db_session, session_id)
        session_state_data = None
        if message_with_state and message_with_state.state:
            try:
                session_state_data = SessionStateData.model_validate(message_with_state.state)
            except ValidationError as err:
                self._log.warning(
                    "Invalid session state for session %s, ignoring: %s", session_id, err.errors()
                )

        project_def = project_manager.get_project(session.project_id)
        project = Project.from_definition(project_def)
        context = StoryContext(project, session_state_data)

        model = (
            create_model_from_db_config(
                model_name=session.config.model_name,
                provider=session.config.provider,
                base_url=session.config.base_url,
                api_key=session.config.api_key,
            )
            if session.config
            else None
        )

        return model, context

    async def _create_model_from_config(
        self, model_name: str, provider: ModelProvider, base_url: str | None, api_key: str | None
    ) -> Model:
        return create_model_from_db_config(
            model_name=model_name,
            provider=provider,
            base_url=base_url,
            api_key=api_key,
        )

    def _perform_eviction(self) -> None:
        cutoff = time.time() - self._max_idle
        to_drop = [sid for sid, (_, ts) in self._engines.items() if ts < cutoff]
        for sid in to_drop:
            self._drop_engine(sid)

    async def _evict_idle(self) -> None:
        while True:
            await asyncio.sleep(30)
            self._perform_eviction()

    def _drop_engine(self, session_id: UUID) -> None:
        self._log.debug(f"Dropping engine for session {session_id}")
        with suppress(KeyError):
            self._engines.pop(session_id)

    def _on_session_deleted(self, message: SessionDeleted) -> None:
        self._drop_engine(message.session_id)

    async def _on_model_config_changed(self, message: SessionModelConfigChangedMessage) -> None:
        session_id = message.session_id
        if session_id not in self._engines:
            self._log.debug(
                f"No active engine for session {session_id}, ignoring model config change"
            )
            return

        self._log.info(f"Model config changed for session {session_id}, updating engine")
        engine, _ = self._engines[session_id]
        new_model = await self._create_model_from_config(
            message.model_name, message.provider, message.base_url, message.api_key
        )
        engine.set_model(new_model)
