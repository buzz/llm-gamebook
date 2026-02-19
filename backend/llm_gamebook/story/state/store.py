from collections.abc import Callable
from typing import cast

from pydantic import BaseModel

from llm_gamebook.story.trait_registry import trait_registry

from .actions import Action
from .session_state import SessionState

type Middleware = Callable[[Store, Action[BaseModel]], Action[BaseModel]]
type Reducer = Callable[[SessionState, Action[BaseModel]], SessionState]
type ReducerRegistry = dict[str, list[Reducer]]

MAX_DISPATCH_DEPTH = 2


class Store:
    """Redux-inspired store for managing session state through actions."""

    def __init__(
        self,
        initial_state: SessionState | None = None,
        middleware: list[Middleware] | None = None,
        reducers: ReducerRegistry | None = None,
    ) -> None:
        self._state = initial_state or SessionState()
        self._middleware = middleware or []
        self._reducers: ReducerRegistry = reducers or {}
        self._dispatch_depth = 0

        self._load_trait_reducers()

    def _load_trait_reducers(self) -> None:
        """Load all registered trait reducers into the store."""
        for action_name, reducers in trait_registry.get_all_reducers().items():
            for reducer in reducers:
                self._register_reducer(action_name, reducer)

    def _register_reducer(self, action_name: str, reducer: Reducer) -> None:
        if action_name not in self._reducers:
            self._reducers[action_name] = []
        self._reducers[action_name].append(reducer)

    def dispatch[T: BaseModel](self, action: Action[T]) -> SessionState:
        """Dispatch an action and return new state."""
        if self._dispatch_depth >= MAX_DISPATCH_DEPTH:
            msg = "Maximum dispatch depth exceeded - possible infinite recursion"
            raise RuntimeError(msg)

        self._dispatch_depth += 1
        try:
            processed_action = cast("Action[BaseModel]", action)
            for mw in self._middleware:
                processed_action = mw(self, processed_action)

            new_state = self._run_reducers(processed_action)
            self._state = new_state
            return new_state
        finally:
            self._dispatch_depth -= 1

    def _run_reducers(self, action: Action[BaseModel]) -> SessionState:
        """Run all registered reducers for an action."""
        reducers = self._reducers.get(action.name, [])
        if not reducers:
            return self._clone_state()

        state = self._clone_state()
        for reducer in reducers:
            state = reducer(state, action)
            if not isinstance(state, SessionState):
                msg = (
                    f"Reducer for '{action.name}' must return a SessionState "
                    f"instance, got {type(state).__name__}"
                )
                raise TypeError(msg)
        return state

    def get_state(self) -> SessionState:
        """Get current state."""
        return self._state

    def _clone_state(self) -> SessionState:
        """Create a new SessionState with same data."""
        json_str = self._state.to_json()
        return SessionState.from_json(json_str)
