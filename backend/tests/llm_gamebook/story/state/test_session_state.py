import pytest

from llm_gamebook.story.errors import EntityFieldNotFoundError
from llm_gamebook.story.state import EntityRef, EntityRefList, SessionState, SessionStateData


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
    ref: EntityRef = {"type": "entity", "target": "npc_1"}
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


def test_full_state_json_roundtrip() -> None:
    """A complete state snapshot roundtrips through JSON losslessly."""
    state = SessionState()
    state.set_field("player_1", "health", 100)
    state.set_field("player_1", "name", "Hero")
    state.set_field("player_1", "target", {"type": "entity", "target": "npc_1"})
    state.set_field("player_1", "enemies", {"type": "entity-list", "target": ["npc_1", "npc_2"]})
    state.set_field("player_1", "score", 42.5)
    state.set_field("player_1", "is_alive", value=True)
    state.set_field("main", "current_node_id", "node_a")

    restored = SessionState.from_json(state.to_json())

    for entity_id in ("player_1", "main"):
        for field_name, value in state.data.entities[entity_id].items():
            assert restored.get_field(entity_id, field_name) == value

    assert restored.to_json() == state.to_json()


def test_full_state_snapshot_contains_all_overrides() -> None:
    """model_dump of the data is a full snapshot, not just the latest change."""
    state = SessionState()
    state.set_field("entity1", "field1", "value1")
    state.set_field("entity2", "field2", 2)
    state.set_field("entity1", "field1", "value1-updated")

    snapshot = state.data.model_dump()

    assert snapshot == {
        "entities": {
            "entity1": {"field1": "value1-updated"},
            "entity2": {"field2": 2},
        }
    }


def test_empty_state_roundtrip() -> None:
    state = SessionState()
    restored = SessionState.from_json(state.to_json())

    assert restored.is_empty()
    assert restored.data.model_dump() == {"entities": {}}
