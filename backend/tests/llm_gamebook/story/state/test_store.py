from typing import cast

import pytest
from pydantic import BaseModel

from llm_gamebook.story.state import (
    Action,
    EndGameAction,
    ForkAction,
    Next,
    ResetGameAction,
    RestoreAction,
    SessionState,
    Store,
)


class DictPayload(BaseModel):
    """Generic payload for ad-hoc actions (e.g., testing)."""

    data: dict[str, object] = {}


def test_store_dispatch_returns_new_state() -> None:
    store = Store()
    action = Action[DictPayload](name="test/action", payload=DictPayload())
    new_state = store.dispatch(action)
    assert isinstance(new_state, SessionState)


def test_store_dispatch_immutability() -> None:
    initial_state = SessionState()
    initial_state.set_field("entity1", "field1", "value1")
    store = Store(initial_state=initial_state)

    original_json = initial_state.to_json()
    action = Action[DictPayload](name="test/action", payload=DictPayload())
    store.dispatch(action)

    assert initial_state.to_json() == original_json


def test_store_get_state_returns_current_state() -> None:
    initial_state = SessionState()
    initial_state.set_field("entity1", "field1", "value1")
    store = Store(initial_state=initial_state)

    state = store.get_state()
    assert state.get_field("entity1", "field1") == "value1"


def test_store_dispatch_depth_protection() -> None:
    store = Store()
    call_count = 0

    def recursive_middleware(s: Store, a: Action[BaseModel], n: Next) -> SessionState:
        nonlocal call_count
        call_count += 1
        if call_count < 12:
            s.dispatch(Action[DictPayload](name="test/another", payload=DictPayload()))
        return n(a)

    store._middleware = [recursive_middleware]

    with pytest.raises(RuntimeError, match="Maximum dispatch depth"):
        store.dispatch(Action[DictPayload](name="test/action", payload=DictPayload()))


def test_store_register_reducer() -> None:
    store = Store()

    def my_reducer(state: SessionState, action: Action[BaseModel]) -> SessionState:
        state.set_field("entity1", "processed", "yes")
        return state

    store._register_reducer("test/action", my_reducer)

    action = Action[DictPayload](name="test/action", payload=DictPayload())
    new_state = store.dispatch(action)
    assert new_state.get_field("entity1", "processed") == "yes"


def test_store_no_reducer_returns_cloned_state() -> None:
    initial_state = SessionState()
    initial_state.set_field("entity1", "field1", "value1")
    store = Store(initial_state=initial_state)

    action = Action[DictPayload](name="test/unregistered", payload=DictPayload())
    new_state = store.dispatch(action)

    assert new_state.get_field("entity1", "field1") == "value1"
    assert new_state is not initial_state


def test_store_multiple_reducers_composition() -> None:
    store = Store()

    def reducer1(state: SessionState, action: Action[BaseModel]) -> SessionState:
        state.set_field("entity1", "field1", "value1")
        return state

    def reducer2(state: SessionState, action: Action[BaseModel]) -> SessionState:
        state.set_field("entity1", "field2", "value2")
        return state

    store._register_reducer("test/action", reducer1)
    store._register_reducer("test/action", reducer2)

    action = Action[DictPayload](name="test/action", payload=DictPayload())
    new_state = store.dispatch(action)

    assert new_state.get_field("entity1", "field1") == "value1"
    assert new_state.get_field("entity1", "field2") == "value2"


def test_store_middleware_chain_order() -> None:
    order: list[str] = []

    def middleware1(s: Store, a: Action[BaseModel], n: Next) -> SessionState:
        order.append("mw1")
        return n(a)

    def middleware2(s: Store, a: Action[BaseModel], n: Next) -> SessionState:
        order.append("mw2")
        return n(a)

    store = Store(middleware=[middleware1, middleware2])
    store.dispatch(Action[DictPayload](name="test/action", payload=DictPayload()))

    assert order == ["mw1", "mw2"]


def test_store_middleware_can_modify_action() -> None:
    def modify_middleware(s: Store, a: Action[BaseModel], n: Next) -> SessionState:
        modified = Action[DictPayload](name="test/modified", payload=DictPayload())
        return n(cast("Action[BaseModel]", modified))

    store = Store(middleware=[modify_middleware])

    captured_name: str = ""

    def capture_reducer(state: SessionState, action: Action[BaseModel]) -> SessionState:
        nonlocal captured_name
        captured_name = action.name
        return state

    store._register_reducer("test/modified", capture_reducer)
    store.dispatch(Action[DictPayload](name="test/original", payload=DictPayload()))

    assert captured_name == "test/modified"


def test_full_dispatch_flow_integration() -> None:
    middleware_log: list[str] = []
    reducer_log: list[str] = []

    def logging_middleware(s: Store, a: Action[BaseModel], n: Next) -> SessionState:
        middleware_log.append(f"mw:{a.name}")
        return n(a)

    def test_reducer(state: SessionState, action: Action[BaseModel]) -> SessionState:
        reducer_log.append(f"reducer:{action.name}")
        if isinstance(action.payload, DictPayload):
            entity_id = action.payload.data.get("entity_id")
            value = action.payload.data.get("value")
            if isinstance(entity_id, str) and isinstance(value, int):
                state.set_field(entity_id, "result", value)
        return state

    initial_state = SessionState()
    initial_state.set_field("entity1", "initial", "yes")

    store = Store(
        initial_state=initial_state,
        middleware=[logging_middleware],
    )
    store._register_reducer("test/flow", test_reducer)

    action = Action[DictPayload](
        name="test/flow", payload=DictPayload(data={"entity_id": "entity1", "value": 42})
    )
    new_state = store.dispatch(action)

    assert middleware_log == ["mw:test/flow"]
    assert reducer_log == ["reducer:test/flow"]
    assert new_state.get_field("entity1", "result") == 42
    assert new_state.get_field("entity1", "initial") == "yes"
    assert new_state is not initial_state


def test_store_reducer_must_return_session_state() -> None:
    store = Store()

    def bad_reducer(state: SessionState, action: Action[BaseModel]) -> object:
        return {"not": "a session state"}

    store._register_reducer("test/bad", bad_reducer)  # type: ignore[arg-type]
    action = Action[DictPayload](name="test/bad", payload=DictPayload())

    with pytest.raises(TypeError, match="must return a SessionState instance"):
        store.dispatch(action)


def test_store_set_state() -> None:
    store = Store()

    new_state = SessionState()
    new_state.set_field("entity1", "restored", value=True)
    store.set_state(new_state)

    assert store.get_state().get_field("entity1", "restored") is True


def test_store_dispatch_reset_game_action_clears_state() -> None:
    initial_state = SessionState()
    initial_state.set_field("entity1", "field1", "value1")
    store = Store(initial_state=initial_state)

    new_state = store.dispatch(ResetGameAction())

    assert new_state.is_empty()
    assert store.get_state().is_empty()


def test_store_dispatch_reset_game_action_is_idempotent() -> None:
    store = Store()

    new_state = store.dispatch(ResetGameAction())

    assert new_state.is_empty()


def test_store_dispatch_unregistered_core_action_preserves_state() -> None:
    initial_state = SessionState()
    initial_state.set_field("entity1", "field1", "value1")
    store = Store(initial_state=initial_state)

    new_state = store.dispatch(EndGameAction(reason="done"))
    assert new_state.get_field("entity1", "field1") == "value1"

    new_state = store.dispatch(RestoreAction(step=0))
    assert new_state.get_field("entity1", "field1") == "value1"

    new_state = store.dispatch(ForkAction(step=-1))
    assert new_state.get_field("entity1", "field1") == "value1"

    assert store.get_state().get_field("entity1", "field1") == "value1"
