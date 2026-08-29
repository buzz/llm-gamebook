import pytest
from pydantic import ValidationError

from llm_gamebook.story.state import (
    Action,
    EndGameAction,
    EndGamePayload,
    ForkAction,
    ResetGameAction,
    ResetGamePayload,
    RestoreAction,
    StepPayload,
)


def test_valid_action_name_with_namespace() -> None:
    action = Action[EndGamePayload](name="graph/transition", payload=EndGamePayload())
    assert action.name == "graph/transition"


def test_invalid_action_name_without_slash() -> None:
    with pytest.raises(ValidationError) as exc_info:
        Action[EndGamePayload](name="invalid", payload=EndGamePayload())
    assert "namespace/action" in str(exc_info.value)


def test_invalid_action_name_not_string() -> None:
    with pytest.raises(ValidationError):
        Action[EndGamePayload](name=123, payload=EndGamePayload())  # type: ignore[arg-type]


def test_action_to_json() -> None:
    action = EndGameAction(reason="victory")
    json_str = action.model_dump_json()
    assert '"name":"core/end-game"' in json_str
    assert '"reason":"victory"' in json_str


def test_action_from_json() -> None:
    json_str = '{"name":"core/end-game","payload":{"reason":"victory"}}'
    action = Action[EndGamePayload].model_validate_json(json_str)
    assert action.name == "core/end-game"
    assert action.payload.reason == "victory"


def test_create_end_game_action_no_reason() -> None:
    action = EndGameAction()
    assert action.name == "core/end-game"
    assert action.payload.reason is None


def test_create_end_game_action_with_reason() -> None:
    action = EndGameAction(reason="player_won")
    assert action.name == "core/end-game"
    assert action.payload.reason == "player_won"


def test_end_game_serialization() -> None:
    action = EndGameAction(reason="victory")
    json_str = action.model_dump_json()
    assert "core/end-game" in json_str
    assert "victory" in json_str


def test_end_game_roundtrip() -> None:
    original = EndGameAction(reason="defeat")
    json_str = original.model_dump_json()
    restored = Action[EndGamePayload].model_validate_json(json_str)
    assert restored.name == original.name
    assert restored.payload.reason == original.payload.reason


def test_create_reset_game_action() -> None:
    action = ResetGameAction()
    assert action.name == "core/reset-game"
    assert action.payload.model_dump() == {}


def test_reset_game_roundtrip() -> None:
    original = ResetGameAction()
    json_str = original.model_dump_json()
    restored: Action[ResetGamePayload] = Action[ResetGamePayload].model_validate_json(json_str)
    assert restored.name == "core/reset-game"


def test_create_restore_action_default_step() -> None:
    action = RestoreAction()
    assert action.name == "core/restore"
    assert action.payload.step == -1


def test_create_restore_action_with_step() -> None:
    action = RestoreAction(step=3)
    assert action.name == "core/restore"
    assert action.payload.step == 3


def test_restore_action_roundtrip() -> None:
    original = RestoreAction(step=7)
    json_str = original.model_dump_json()
    restored = Action[StepPayload].model_validate_json(json_str)
    assert restored.name == "core/restore"
    assert restored.payload.step == 7


def test_create_fork_action_default_step() -> None:
    action = ForkAction()
    assert action.name == "core/fork"
    assert action.payload.step == -1


def test_create_fork_action_with_step() -> None:
    action = ForkAction(step=2)
    assert action.name == "core/fork"
    assert action.payload.step == 2


def test_fork_action_roundtrip() -> None:
    original = ForkAction(step=0)
    json_str = original.model_dump_json()
    restored = Action[StepPayload].model_validate_json(json_str)
    assert restored.name == "core/fork"
    assert restored.payload.step == 0
