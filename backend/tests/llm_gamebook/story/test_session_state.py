import pytest

from llm_gamebook.story.errors import EntityFieldNotFoundError
from llm_gamebook.story.session_state import (
    EntityRefList,
    EntityRefSingle,
    SessionState,
    SessionStateData,
)


def test_set_and_get_field() -> None:
    state = SessionState()
    state.set_field("player_1", "health", 100)
    assert state.get_field("player_1", "health") == 100


def test_get_field_not_set() -> None:
    state = SessionState()
    with pytest.raises(EntityFieldNotFoundError):
        state.get_field("player_1", "health")


def test_set_multiple_fields_same_entity() -> None:
    state = SessionState()
    state.set_field("player_1", "health", 100)
    state.set_field("player_1", "name", "Hero")
    assert state.get_field("player_1", "health") == 100
    assert state.get_field("player_1", "name") == "Hero"


def test_set_multiple_entities() -> None:
    state = SessionState()
    state.set_field("player_1", "health", 100)
    state.set_field("player_2", "health", 50)
    assert state.get_field("player_1", "health") == 100
    assert state.get_field("player_2", "health") == 50


def test_overwrite_field() -> None:
    state = SessionState()
    state.set_field("player_1", "health", 100)
    state.set_field("player_1", "health", 50)
    assert state.get_field("player_1", "health") == 50


def test_to_json_and_from_json() -> None:
    state = SessionState()
    state.set_field("player_1", "health", 100)
    state.set_field("player_1", "name", "Hero")

    json_str = state.to_json()
    restored = SessionState.from_json(json_str)

    assert restored.get_field("player_1", "health") == 100
    assert restored.get_field("player_1", "name") == "Hero"


def test_entity_ref_single() -> None:
    state = SessionState()
    ref: EntityRefSingle = {"type": "entity", "target": "npc_1"}
    state.set_field("player_1", "target", ref)

    result = state.get_field("player_1", "target")
    assert result == ref


def test_entity_ref_list() -> None:
    state = SessionState()
    ref: EntityRefList = {"type": "entity-list", "target": ["npc_1", "npc_2"]}
    state.set_field("player_1", "enemies", ref)

    result = state.get_field("player_1", "enemies")
    assert result == ref


def test_init_with_session_state_data() -> None:
    data = SessionStateData(entities={"player_1": {"health": 100}})
    state = SessionState(data)

    assert state.get_field("player_1", "health") == 100


def test_valid_entity_ref() -> None:
    data = SessionStateData(
        entities={
            "player_1": {
                "health": 100,
                "name": "Hero",
                "is_alive": True,
                "score": 99.5,
                "target": {"type": "entity", "target": "npc_1"},
            }
        }
    )
    assert data.entities["player_1"]["health"] == 100
    assert data.entities["player_1"]["target"] == {"type": "entity", "target": "npc_1"}
