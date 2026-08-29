from datetime import UTC, datetime, timedelta
from uuid import uuid4

from pydantic import BaseModel

from llm_gamebook.message_bus import MessageBus
from llm_gamebook.story.state import (
    Action,
    ActionDispatched,
    EndGameAction,
    Next,
    SessionState,
    Store,
)
from llm_gamebook.story.state.middleware import message_bus_publisher_middleware
from llm_gamebook.story.traits.graph import GraphTransitionAction


class DictPayload(BaseModel):
    """Generic payload for ad-hoc actions (e.g., testing)."""

    data: dict[str, object] = {}


def make_action(name: str, data: dict[str, object] | None = None) -> Action[DictPayload]:
    return Action[DictPayload](name=name, payload=DictPayload(data=data or {}))


def set_field_reducer(state: SessionState, action: Action[BaseModel]) -> SessionState:
    if isinstance(action.payload, DictPayload) and "entity_id" in action.payload.data:
        state.set_field(str(action.payload.data["entity_id"]), "flag", "set")
    return state


async def test_publisher_message_fields_match_action(message_bus: MessageBus) -> None:
    session_id = uuid4()
    store = Store(middleware=[message_bus_publisher_middleware(message_bus, session_id)])

    received: list[ActionDispatched] = []
    message_bus.subscribe(ActionDispatched, received.append)

    store.dispatch(GraphTransitionAction(entity_id="main", to="node_b"))

    assert len(received) == 1
    message = received[0]
    assert message.session_id == session_id
    assert message.action_type == "graph/transition"
    assert message.payload == {"entity_id": "main", "to": "node_b"}


async def test_publisher_publishes_before_reducer(message_bus: MessageBus) -> None:
    session_id = uuid4()
    store = Store(middleware=[message_bus_publisher_middleware(message_bus, session_id)])
    store._register_reducer("test/flag", set_field_reducer)

    states_seen: list[SessionState] = []
    message_bus.subscribe(ActionDispatched, lambda msg: states_seen.append(store.get_state()))

    store.dispatch(make_action("test/flag", {"entity_id": "entity1"}))

    assert len(states_seen) == 1
    # At publish time the reducer has not run yet
    assert states_seen[0].data.entities == {}
    # After dispatch the reducer effect is in place
    assert store.get_state().get_field("entity1", "flag") == "set"


async def test_additional_middleware_dispatches_are_published(message_bus: MessageBus) -> None:
    session_id = uuid4()
    received: list[ActionDispatched] = []
    message_bus.subscribe(ActionDispatched, received.append)

    def extra_dispatch(s: Store, a: Action[BaseModel], n: Next) -> SessionState:
        state = n(a)
        if a.name == "test/first":
            s.dispatch(make_action("test/second"))
        return state

    store = Store(
        middleware=[message_bus_publisher_middleware(message_bus, session_id), extra_dispatch]
    )

    store.dispatch(make_action("test/first"))

    assert [m.action_type for m in received] == ["test/first", "test/second"]


async def test_publisher_timestamp_is_utc(message_bus: MessageBus) -> None:
    session_id = uuid4()
    store = Store(middleware=[message_bus_publisher_middleware(message_bus, session_id)])

    received: list[ActionDispatched] = []
    message_bus.subscribe(ActionDispatched, received.append)

    before = datetime.now(UTC)
    store.dispatch(make_action("test/action"))

    message = received[0]
    assert message.timestamp.tzinfo is not None
    assert message.timestamp.utcoffset() == timedelta(0)
    assert message.timestamp >= before


async def test_no_filter_publishes_all_actions(message_bus: MessageBus) -> None:
    session_id = uuid4()
    store = Store(middleware=[message_bus_publisher_middleware(message_bus, session_id)])

    received: list[ActionDispatched] = []
    message_bus.subscribe(ActionDispatched, received.append)

    store.dispatch(EndGameAction(reason="done"))
    store.dispatch(GraphTransitionAction(entity_id="main", to="node_b"))
    store.dispatch(make_action("audio/play"))

    assert [m.action_type for m in received] == ["core/end-game", "graph/transition", "audio/play"]


async def test_namespace_filter(message_bus: MessageBus) -> None:
    session_id = uuid4()
    store = Store(
        middleware=[
            message_bus_publisher_middleware(message_bus, session_id, filter_pattern="core/*")
        ]
    )

    received: list[ActionDispatched] = []
    message_bus.subscribe(ActionDispatched, received.append)

    store.dispatch(EndGameAction(reason="done"))
    store.dispatch(GraphTransitionAction(entity_id="main", to="node_b"))

    assert [m.action_type for m in received] == ["core/end-game"]


async def test_list_filter(message_bus: MessageBus) -> None:
    session_id = uuid4()
    store = Store(
        middleware=[
            message_bus_publisher_middleware(
                message_bus, session_id, filter_pattern=["core/*", "graph/*"]
            )
        ]
    )

    received: list[ActionDispatched] = []
    message_bus.subscribe(ActionDispatched, received.append)

    store.dispatch(EndGameAction(reason="done"))
    store.dispatch(GraphTransitionAction(entity_id="main", to="node_b"))
    store.dispatch(make_action("audio/play"))

    assert [m.action_type for m in received] == ["core/end-game", "graph/transition"]


async def test_filtered_out_action_still_reaches_reducers(message_bus: MessageBus) -> None:
    session_id = uuid4()
    store = Store(
        middleware=[
            message_bus_publisher_middleware(message_bus, session_id, filter_pattern="core/*")
        ]
    )
    store._register_reducer("test/flag", set_field_reducer)

    received: list[ActionDispatched] = []
    message_bus.subscribe(ActionDispatched, received.append)

    store.dispatch(make_action("test/flag", {"entity_id": "entity1"}))

    assert received == []
    assert store.get_state().get_field("entity1", "flag") == "set"


def test_no_op_without_bus() -> None:
    store = Store(middleware=[message_bus_publisher_middleware(None, uuid4())])
    store._register_reducer("test/flag", set_field_reducer)

    store.dispatch(make_action("test/flag", {"entity_id": "entity1"}))

    assert store.get_state().get_field("entity1", "flag") == "set"


async def test_no_op_without_session_id(message_bus: MessageBus) -> None:
    store = Store(middleware=[message_bus_publisher_middleware(message_bus, None)])
    store._register_reducer("test/flag", set_field_reducer)

    received: list[ActionDispatched] = []
    message_bus.subscribe(ActionDispatched, received.append)

    store.dispatch(make_action("test/flag", {"entity_id": "entity1"}))

    assert received == []
    assert store.get_state().get_field("entity1", "flag") == "set"


async def test_multiple_subscribers_receive_message(message_bus: MessageBus) -> None:
    session_id = uuid4()
    store = Store(middleware=[message_bus_publisher_middleware(message_bus, session_id)])

    first: list[ActionDispatched] = []
    second: list[ActionDispatched] = []
    message_bus.subscribe(ActionDispatched, first.append)
    message_bus.subscribe(ActionDispatched, second.append)

    store.dispatch(EndGameAction(reason="done"))

    assert [m.action_type for m in first] == ["core/end-game"]
    assert [m.action_type for m in second] == ["core/end-game"]
