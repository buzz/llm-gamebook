import asyncio
import time
from contextlib import suppress
from types import TracebackType
from typing import TYPE_CHECKING, Self
from uuid import UUID

from pydantic_ai.models import Model

from llm_gamebook.engine import StoryEngine
from llm_gamebook.logger import logger
from llm_gamebook.message_bus import BusSubscriber, MessageBus

if TYPE_CHECKING:
    from llm_gamebook.story.state import StoryState


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
        model: Model,
        state: "StoryState",
    ) -> StoryEngine:
        created: bool = False
        try:
            # Retrieve engine...
            engine, _ = self._engines[session_id]
        except KeyError:
            # ...or create new
            engine = StoryEngine(session_id, model, state, self._bus)
            created = True

        self._engines[session_id] = (engine, time.time())  # bump last used

        if created:
            self._bus.publish("engine.created", session_id)

        return engine

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
