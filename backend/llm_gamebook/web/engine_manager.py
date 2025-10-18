import asyncio
import contextlib
import time
from uuid import UUID

from pydantic_ai.models import Model

from llm_gamebook.engine import StoryEngine
from llm_gamebook.story.state import StoryState


class EngineManager:
    def __init__(self, max_idle_seconds: int = 600) -> None:
        self._engines: dict[UUID, tuple[StoryEngine, float]] = {}  # engine, last_used
        self._max_idle = max_idle_seconds
        self._evict_task = asyncio.create_task(self._evict_idle())

    async def close(self) -> None:
        if self._evict_task and not self._evict_task.done():
            self._evict_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._evict_task

    async def get_or_create(
        self, chat_id: UUID, model: Model, state: StoryState, *, streaming: bool
    ) -> StoryEngine:
        now = time.time()
        if chat_id not in self._engines:
            engine = StoryEngine(chat_id, model, state, streaming=streaming)
            await engine.init()
            self._engines[chat_id] = (engine, now)
        else:
            engine, _ = self._engines[chat_id]
            self._engines[chat_id] = (engine, now)  # bump last_used
        return self._engines[chat_id][0]

    async def _evict_idle(self) -> None:
        while True:
            await asyncio.sleep(30)
            cutoff = time.time() - self._max_idle
            to_drop = [cid for cid, (_, ts) in self._engines.items() if ts < cutoff]
            for cid in to_drop:
                self._engines.pop(cid, None)
