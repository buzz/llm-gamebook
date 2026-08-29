import asyncio
import inspect
from collections import defaultdict
from contextlib import suppress
from types import TracebackType
from typing import TYPE_CHECKING, Self, cast

from llm_gamebook.logger import logger

from .messages import BaseMessage, MessageHandler

if TYPE_CHECKING:
    from collections.abc import Coroutine


class MessageBus:
    def __init__(self) -> None:
        self._log = logger.getChild("message-bus")
        self._subs: dict[type[BaseMessage], list[MessageHandler[BaseMessage]]] = defaultdict(list)
        self._tasks: set[asyncio.Task[None]] = set()
        self._lock = asyncio.Lock()
        self._loop: asyncio.AbstractEventLoop | None = None
        with suppress(RuntimeError):
            self._loop = asyncio.get_running_loop()

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self.unsubscribe_all()
        await self.wait_all()

    def subscribe[T: BaseMessage](self, message_cls: type[T], handler: MessageHandler[T]) -> None:
        self._subs[message_cls].append(cast("MessageHandler[BaseMessage]", handler))

    def unsubscribe[T: BaseMessage](self, message_cls: type[T], handler: MessageHandler[T]) -> None:
        if message_cls in self._subs:
            with suppress(ValueError):
                self._subs[message_cls].remove(cast("MessageHandler[BaseMessage]", handler))
            if not self._subs[message_cls]:
                del self._subs[message_cls]

    def unsubscribe_all(self) -> None:
        """Remove all subscriptions."""
        self._subs.clear()

    def publish(self, message: BaseMessage) -> None:
        self._log.debug("Publish %s", message)

        if handlers := self._subs.get(type(message)):
            for handler in handlers:
                if inspect.iscoroutinefunction(handler):
                    self._schedule_async_handler(handler, message)
                else:
                    try:
                        handler(message)
                    except Exception:
                        self._log.error("Sync handler failed:")
                        raise

    def _schedule_async_handler(
        self, handler: MessageHandler[BaseMessage], message: BaseMessage
    ) -> None:
        """Schedule an async handler, from the current thread or a worker thread.

        Pydantic-ai executes sync tool functions in a worker thread, so
        publishes may originate outside any running event loop (e.g. story
        actions dispatched by tools). In that case the handler task is
        scheduled on the loop this bus is bound to.
        """
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            self._schedule_off_loop(handler, message)
            return
        self._loop = loop
        self._spawn_async_handler(handler, message)

    def _schedule_off_loop(
        self, handler: MessageHandler[BaseMessage], message: BaseMessage
    ) -> None:
        """Schedule an async handler task on the loop this bus is bound to."""
        loop = self._loop
        if loop is None or loop.is_closed():
            self._log.error(
                "Cannot deliver async handler for %s: no running or bound event loop",
                type(message).__name__,
            )
            return
        try:
            loop.call_soon_threadsafe(self._spawn_async_handler, handler, message)
        except RuntimeError:
            self._log.error(
                "Cannot deliver async handler for %s: bound event loop closed",
                type(message).__name__,
            )

    def _spawn_async_handler(
        self, handler: MessageHandler[BaseMessage], message: BaseMessage
    ) -> None:
        coroutine = cast("Coroutine[None, None, None]", handler(message))
        task = asyncio.create_task(coroutine)
        self._tasks.add(task)
        task.add_done_callback(self._handler_done_callback)

    def _handler_done_callback(self, task: asyncio.Task[None]) -> None:
        self._tasks.discard(task)
        if (exc := task.exception()) is not None:
            tb = exc.__traceback__
            self._log.error("Async handler failed:", exc_info=(type(exc), exc, tb))

    async def wait_all(self) -> None:
        """Wait for all currently running handler tasks."""
        async with self._lock:
            if self._tasks:
                await asyncio.gather(*self._tasks, return_exceptions=True)
