import asyncio
import inspect
import weakref
from typing import TYPE_CHECKING, cast

from .messages import BaseMessage, MessageHandler

if TYPE_CHECKING:
    from .message_bus import MessageBus

type SubTuple = tuple[
    type[BaseMessage],
    weakref.ReferenceType[MessageHandler[BaseMessage]],
    MessageHandler[BaseMessage],
]
type SubList = list[SubTuple]
"""List of (topic, ref, wrapper)"""


class BusSubscriber:
    """Mixin that subscribes automatically and tracks weakrefs to handlers."""

    _bus: "MessageBus"  # must be set in subclass

    def _subscribe[T: BaseMessage](self, message_cls: type[T], handler: MessageHandler[T]) -> None:
        if not hasattr(self, "_subs"):
            self._subs: SubList = []
            # register automatic cleanup when this object is GC'd
            weakref.finalize(self, self._finalizer, weakref.ref(self))

        # create weakref to handler
        ref: weakref.WeakMethod[MessageHandler[T]] | weakref.ReferenceType[MessageHandler[T]]
        if hasattr(handler, "__self__") and hasattr(handler, "__func__"):
            # bound method
            ref = weakref.WeakMethod(handler)
        else:
            # regular function
            ref = weakref.ref(handler)

        # create wrapper that does NOT capture `self`
        wrapper = self._make_weak_wrapper(message_cls, ref, self._bus)

        # subscribe wrapper to the bus, and keep wrapper stored
        self._bus.subscribe(message_cls, wrapper)
        self._subs.append(cast("SubTuple", (message_cls, ref, wrapper)))

    def _make_weak_wrapper[T: BaseMessage](
        self,
        message_cls: type[T],
        ref: weakref.ReferenceType[MessageHandler[T]],
        bus: "MessageBus",
    ) -> MessageHandler[T]:
        # Note: do NOT capture `self` here.
        # The wrapper captures only ref, topic, and bus (bus is fine: it's a long-lived object).
        async def wrapper(message: T) -> None:
            target = ref()
            if target is None:
                # target gone → unsubscribe this wrapper from the bus only
                bus.unsubscribe(message_cls, wrapper)
                return

            # call the target appropriately depending on whether it's async
            if inspect.iscoroutinefunction(target):
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
