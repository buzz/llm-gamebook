import asyncio
import weakref
from collections import defaultdict
from collections.abc import Awaitable, Callable
from contextlib import suppress
from fnmatch import fnmatch
from types import TracebackType
from typing import Self

from llm_gamebook.logger import logger

type MessageHandler = Callable[[object], Awaitable[None]] | Callable[[object], None]


class MessageBus:
    def __init__(self) -> None:
        self._log = logger.getChild("message-bus")
        self._subs: dict[str, list[MessageHandler]] = defaultdict(list)
        self._tasks: set[asyncio.Task[None]] = set()
        self._lock = asyncio.Lock()

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

    def subscribe(self, topic: str, handler: MessageHandler) -> None:
        self._subs[topic].append(handler)

    def unsubscribe(self, topic: str, handler: MessageHandler) -> None:
        if topic in self._subs:
            with suppress(ValueError):
                self._subs[topic].remove(handler)
            if not self._subs[topic]:
                del self._subs[topic]

    def unsubscribe_all(self) -> None:
        """Remove all subscriptions."""
        self._subs.clear()

    def publish(self, topic: str, message: object = None) -> None:
        self._log.debug("Publish %s", topic)
        for pat, handlers in list(self._subs.items()):
            if fnmatch(topic, pat):
                for handler in handlers:
                    if asyncio.iscoroutinefunction(handler):
                        task = asyncio.create_task(handler(message))
                        self._tasks.add(task)
                        task.add_done_callback(self._handler_done_callback)
                    else:
                        try:
                            handler(message)
                        except Exception:
                            self._log.error("Sync handler failed:")
                            raise

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


class BusSubscriber:
    """Mixin that subscribes automatically and tracks weakrefs to handlers."""

    _bus: "MessageBus"  # must be set in subclass

    def _subscribe(self, topic: str, handler: MessageHandler) -> None:
        if not hasattr(self, "_subs"):
            # list of (topic, ref, wrapper)
            self._subs: list[tuple[str, weakref.ReferenceType[MessageHandler], MessageHandler]] = []
            # register automatic cleanup when this object is GC'd
            weakref.finalize(self, self._finalizer, weakref.ref(self))

        # create weakref to handler
        ref: weakref.WeakMethod[MessageHandler] | weakref.ReferenceType[MessageHandler]
        if hasattr(handler, "__self__") and hasattr(handler, "__func__"):
            # bound method
            ref = weakref.WeakMethod(handler)
        else:
            # regular function
            ref = weakref.ref(handler)

        # create wrapper that does NOT capture `self`
        wrapper = self._make_weak_wrapper(topic, ref, self._bus)

        # subscribe wrapper to the bus, and keep wrapper stored
        self._bus.subscribe(topic, wrapper)
        self._subs.append((topic, ref, wrapper))

    def _make_weak_wrapper(
        self,
        topic: str,
        ref: weakref.ReferenceType[MessageHandler],
        bus: "MessageBus",
    ) -> MessageHandler:
        # Note: do NOT capture `self` here.
        # The wrapper captures only ref, topic, and bus (bus is fine: it's a long-lived object).
        async def wrapper(message: object) -> None:
            target = ref()
            if target is None:
                # target gone → unsubscribe this wrapper from the bus only
                bus.unsubscribe(topic, wrapper)
                return

            # call the target appropriately depending on whether it's async
            if asyncio.iscoroutinefunction(target):
                await target(message)
            else:
                # run blocking sync handlers off the event loop
                await asyncio.to_thread(target, message)

        # mark the wrapper with an attribute so we can introspect it if needed
        wrapper.__wrapped_ref__ = ref  # type: ignore[attr-defined]
        return wrapper

    def close(self) -> None:
        """Explicitly remove all subscriptions (sync)."""
        self._unsubscribe_all()

    async def aclose(self) -> None:
        """Explicitly remove all subscriptions (async version)."""
        # If the bus ever needs async cleanup, this allows uniform await usage.
        self._unsubscribe_all()

    def _unsubscribe_all(self) -> None:
        if not hasattr(self, "_subs"):
            return
        for topic, _, wrapper in list(self._subs):
            self._bus.unsubscribe(topic, wrapper)

        self._subs.clear()

    @staticmethod
    def _finalizer(self_ref: weakref.ReferenceType["BusSubscriber"]) -> None:
        self = self_ref()
        if self is not None:
            self._unsubscribe_all()
