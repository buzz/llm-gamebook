import asyncio
import time
from contextlib import suppress
from pathlib import Path
from types import TracebackType
from typing import Self
from uuid import UUID

from pydantic_ai.models import Model
from sqlalchemy.orm import selectinload
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession as AsyncDbSession

from llm_gamebook.db.models import Session
from llm_gamebook.engine import StoryEngine
from llm_gamebook.logger import logger
from llm_gamebook.message_bus import BusSubscriber, MessageBus
from llm_gamebook.story.project import Project
from llm_gamebook.story.state import StoryState
from llm_gamebook.web.model_factory import create_model_from_db_config


class EngineManager(BusSubscriber):
    def __init__(self, bus: MessageBus, max_idle_seconds: int = 600) -> None:
        self._log = logger.getChild("engine-manager")

        self._bus = bus
        self._engines: dict[UUID, tuple[StoryEngine, float]] = {}  # engine, last_used
        self._max_idle = max_idle_seconds
        self._evict_task = asyncio.create_task(self._evict_idle())

        self._subscribe("engine.session.deleted", self._drop_engine)

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
    ) -> StoryEngine:
        created: bool = False
        try:
            engine, _ = self._engines[session_id]
        except KeyError:
            model, state = await self._create_model_and_state(session_id, db_session)
            engine = StoryEngine(session_id, model, state, self._bus)
            created = True

        self._engines[session_id] = (engine, time.time())

        if created:
            self._bus.publish("engine.created", session_id)

        return engine

    async def _create_model_and_state(
        self,
        session_id: UUID,
        db_session: AsyncDbSession,
    ) -> tuple[Model, StoryState]:
        statement = select(Session).where(Session.id == session_id)
        statement = statement.options(selectinload(Session.config))  # type: ignore[arg-type]
        result = await db_session.exec(statement)
        session = result.one_or_none()

        if not session or not session.config:
            msg = f"Session {session_id} or its config not found"
            raise ValueError(msg)

        project_path = Path(Path.home() / "llm/llm-gamebook/llm-gamebook/examples/broken-bulb")
        state = StoryState(Project.from_path(project_path))

        model = create_model_from_db_config(
            model_name=session.config.model_name,
            provider=session.config.provider,
            base_url=session.config.base_url,
            api_key=session.config.api_key,
        )

        return model, state

    async def _evict_idle(self) -> None:
        while True:
            await asyncio.sleep(30)
            cutoff = time.time() - self._max_idle
            to_drop = [sid for sid, (_, ts) in self._engines.items() if ts < cutoff]
            for sid in to_drop:
                self._drop_engine(sid)

    def _drop_engine(self, session_id: object) -> None:
        if not isinstance(session_id, UUID):
            msg = f"Invalid message type for engine.session.deleted: {type(session_id)}"
            raise TypeError(msg)

        self._log.debug(f"Dropping engine for session {session_id}")
        with suppress(KeyError):
            self._engines.pop(session_id)
