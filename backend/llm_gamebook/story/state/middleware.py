import fnmatch
import logging
from datetime import UTC, datetime
from typing import TYPE_CHECKING
from uuid import UUID

from pydantic import BaseModel

from llm_gamebook.message_bus import MessageBus

from .actions import Action
from .messages import ActionDispatched
from .session_state import SessionState
from .store import Middleware, Next, Store
from .triggers import dispatch_triggered_actions

if TYPE_CHECKING:
    from llm_gamebook.story.context import StoryContext

logger = logging.getLogger(__name__)

type FilterPattern = str | list[str]


def logging_middleware(store: Store, action: Action[BaseModel], next_chain: Next) -> SessionState:
    """Log action type and payload before dispatch."""
    logger.info("Action dispatched: %s, payload: %s", action.name, action.payload)
    return next_chain(action)


def _matches_filter(action_name: str, filter_pattern: FilterPattern | None) -> bool:
    """Check if an action name matches the given glob filter pattern(s)."""
    if filter_pattern is None:
        return True
    patterns = [filter_pattern] if isinstance(filter_pattern, str) else filter_pattern
    return any(fnmatch.fnmatch(action_name, pattern) for pattern in patterns)


def message_bus_publisher_middleware(
    bus: MessageBus | None,
    session_id: UUID | None,
    filter_pattern: FilterPattern | None = None,
) -> Middleware:
    """Create middleware that publishes ``ActionDispatched`` messages to the message bus.

    When the middleware is bound (both ``bus`` and ``session_id`` are set), it
    publishes an ``ActionDispatched`` message for each dispatched action whose
    name matches the optional glob filter pattern(s) (``None`` publishes all).
    The message is published before the rest of the chain runs, so reducers
    have not applied their state change yet. When unbound, it returns a
    pass-through no-op middleware.
    """
    if bus is None or session_id is None:

        def pass_through(store: Store, action: Action[BaseModel], next_chain: Next) -> SessionState:
            return next_chain(action)

        return pass_through

    def publisher(store: Store, action: Action[BaseModel], next_chain: Next) -> SessionState:
        if _matches_filter(action.name, filter_pattern):
            bus.publish(
                ActionDispatched(
                    session_id=session_id,
                    action_type=action.name,
                    payload=action.payload.model_dump(mode="json"),
                    timestamp=datetime.now(UTC),
                )
            )
        return next_chain(action)

    return publisher


def trigger_eval_middleware(story_context: "StoryContext") -> Middleware:
    """Create trigger evaluation middleware bound to a story context.

    After each action's state changes are committed, all project triggers are
    evaluated and triggers with true conditions dispatch their actions.
    """

    def middleware(store: Store, action: Action[BaseModel], next_chain: Next) -> SessionState:
        state = next_chain(action)
        dispatch_triggered_actions(store, story_context)
        return state

    return middleware


def auto_save_middleware(store: Store, action: Action[BaseModel], next_chain: Next) -> SessionState:
    """Stub middleware for auto-save functionality."""
    return next_chain(action)
