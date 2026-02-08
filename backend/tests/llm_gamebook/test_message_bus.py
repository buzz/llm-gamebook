import asyncio
import gc
import weakref

from llm_gamebook.message_bus import BusSubscriber, MessageBus


class DummySubscriber(BusSubscriber):
    def __init__(self, bus: MessageBus):
        self._bus = bus
        self.messages: list[str] = []
        self._subscribe("ping", self.on_ping)

    async def on_ping(self, msg: object) -> None:
        assert isinstance(msg, str)
        self.messages.append(msg)


async def test_explicit_close_removes_subscription() -> None:
    bus = MessageBus()
    sub = DummySubscriber(bus)

    bus.publish("ping", "one")
    await bus.wait_all()
    assert sub.messages == ["one"]

    sub.close()

    bus.publish("ping", "two")
    await bus.wait_all()
    # No further messages after close
    assert sub.messages == ["one"]


async def test_gc_finalizer_removes_subscription() -> None:
    bus = MessageBus()

    sub = DummySubscriber(bus)
    ref = weakref.ref(sub)

    # Let it handle one message
    bus.publish("ping", "alpha")
    await bus.wait_all()
    assert sub.messages == ["alpha"]

    # Drop all strong references
    del sub
    gc.collect()
    await asyncio.sleep(0)  # let finalizer run

    # subscriber must be GC'd
    assert ref() is None

    # No handler should remain
    bus.publish("ping", "beta")
    await bus.wait_all()

    # If the handler were still present, the bus would error (no instance) or leak message
    # We confirm via bus internals: _subs should be empty or topic removed.
    assert not bus._subs  # topic removed by wrapper after weakref dead


async def test_multiple_subscribers_cleanup_independent() -> None:
    bus = MessageBus()

    s1 = DummySubscriber(bus)
    s2 = DummySubscriber(bus)
    r1, _r2 = weakref.ref(s1), weakref.ref(s2)

    bus.publish("ping", "x")
    await bus.wait_all()
    assert s1.messages == ["x"]
    assert s2.messages == ["x"]

    # Delete only one subscriber
    del s1
    gc.collect()
    await asyncio.sleep(0)

    # Remaining subscriber still works
    bus.publish("ping", "y")
    await bus.wait_all()
    assert r1() is None
    assert s2.messages == ["x", "y"]

    # Bus should still have one subscriber
    assert "ping" in bus._subs
    assert len(bus._subs["ping"]) == 1

    s2.close()
    assert not bus._subs
