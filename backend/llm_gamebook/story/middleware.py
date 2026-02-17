import logging

from pydantic import BaseModel

from llm_gamebook.story.actions import Action
from llm_gamebook.story.store import Store

logger = logging.getLogger(__name__)


def logging_middleware(store: Store, action: Action[BaseModel]) -> Action[BaseModel]:
    """Log action type and payload before dispatch."""
    logger.info("Action dispatched: %s, payload: %s", action.name, action.payload)
    return action


def message_bus_publisher_middleware(store: Store, action: Action[BaseModel]) -> Action[BaseModel]:
    """Stub middleware for message bus publishing (Stage 6)."""
    return action


def trigger_eval_middleware(store: Store, action: Action[BaseModel]) -> Action[BaseModel]:
    """Stub middleware for trigger evaluation (Stage 4)."""
    return action


def auto_save_middleware(store: Store, action: Action[BaseModel]) -> Action[BaseModel]:
    """Stub middleware for auto-save functionality."""
    return action
