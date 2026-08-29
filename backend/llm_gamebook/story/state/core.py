"""State reducers for built-in core game actions."""

from pydantic import BaseModel

from .actions import Action
from .session_state import SessionState

CORE_RESET_GAME = "core/reset-game"
"""Action name for resetting the game to project defaults."""


def reset_game_reducer(state: SessionState, action: Action[BaseModel]) -> SessionState:
    """Reducer for core/reset-game.

    Clears all session state, causing every effective field to fall back to
    its project default.
    """
    return SessionState()
