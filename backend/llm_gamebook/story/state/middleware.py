import logging
from typing import TYPE_CHECKING

from pydantic import BaseModel

from .actions import Action
from .session_state import SessionState
from .store import Middleware, Next, Store
from .triggers import dispatch_triggered_actions

if TYPE_CHECKING:
    from llm_gamebook.story.context import StoryContext

logger = logging.getLogger(__name__)


def logging_middleware(store: Store, action: Action[BaseModel], next_chain: Next) -> SessionState:
    """Log action type and payload before dispatch."""
    logger.info("Action dispatched: %s, payload: %s", action.name, action.payload)
    return next_chain(action)


def message_bus_publisher_middleware(
    store: Store, action: Action[BaseModel], next_chain: Next
) -> SessionState:
    """Stub middleware for message bus publishing (Stage 6)."""
    return next_chain(action)


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
