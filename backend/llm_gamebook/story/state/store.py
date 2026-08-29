from collections.abc import Callable
from typing import cast

from pydantic import BaseModel

from llm_gamebook.story.trait_registry import trait_registry

from .actions import Action
from .session_state import SessionState

type Next = Callable[[Action[BaseModel]], SessionState]
"""Continuation of the middleware chain, eventually running the reducers."""
type Middleware = Callable[[Store, Action[BaseModel], Next], SessionState]
type Reducer = Callable[[SessionState, Action[BaseModel]], SessionState]
type ReducerRegistry = dict[str, list[Reducer]]

MAX_DISPATCH_DEPTH = 10


class Store:
    """Redux-inspired store for managing session state through actions.

    Middleware uses the onion model: each middleware wraps the rest of the
    chain, so it may run code before and/or after the reducers have applied
    the action. Nested dispatches (e.g. middleware dispatching follow-up
    actions) re-enter the full chain, are tracked via
    :attr:`active_action_types`, and are bounded by MAX_DISPATCH_DEPTH as a
    recursion backstop.
    """

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
        self._active_action_types: set[str] | None = None

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

    @property
    def active_action_types(self) -> frozenset[str]:
        """Action names dispatched in the current (possibly nested) dispatch chain.

        Empty outside of a dispatch. Grows as middleware dispatches nested
        actions; resets when the outermost dispatch completes.
        """
        if self._active_action_types is None:
            return frozenset()
        return frozenset(self._active_action_types)

    def dispatch[T: BaseModel](self, action: Action[T]) -> SessionState:
        """Dispatch an action through middleware and reducers, returning the new state."""
        if self._dispatch_depth >= MAX_DISPATCH_DEPTH:
            msg = "Maximum dispatch depth exceeded - possible infinite recursion"
            raise RuntimeError(msg)

        is_top_level = self._active_action_types is None
        if self._active_action_types is None:
            self._active_action_types = {action.name}
        else:
            self._active_action_types.add(action.name)
        self._dispatch_depth += 1
        try:
            return self._dispatch_chain(cast("Action[BaseModel]", action))
        finally:
            self._dispatch_depth -= 1
            if is_top_level:
                self._active_action_types = None

    def _dispatch_chain(self, action: Action[BaseModel]) -> SessionState:
        """Build and run the onion middleware chain around the reducers."""
        chain: Next = self._commit_action
        for mw in reversed(self._middleware):
            chain = self._wrap_middleware(mw, chain)
        return chain(action)

    def _wrap_middleware(self, mw: Middleware, next_chain: Next) -> Next:
        def wrapped(action: Action[BaseModel]) -> SessionState:
            return mw(self, action, next_chain)

        return wrapped

    def _commit_action(self, action: Action[BaseModel]) -> SessionState:
        """Run the reducers for an action and commit the resulting state."""
        new_state = self._run_reducers(action)
        self._state = new_state
        return new_state

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
