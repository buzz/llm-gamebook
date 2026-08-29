"""Resolution and write-guard behavior of dynamic (=`expression`) entity fields."""

import pytest

from llm_gamebook.story.context import StoryContext
from llm_gamebook.story.errors import (
    DynamicFieldEvalError,
    DynamicFieldReadOnlyError,
    EntityFieldNotFoundError,
)
from llm_gamebook.story.schemas import Project, ProjectSource
from llm_gamebook.story.state import EndGameAction, ResetGameAction, SessionState, SessionStateData
from llm_gamebook.story.template_view import EntityView
from llm_gamebook.story.traits.graph import GraphTransitionAction


def _player_project_data(
    extra_player_fields: dict[str, object] | None = None,
    instructions: str | None = None,
) -> dict[str, object]:
    player: dict[str, object] = {
        "id": "player",
        "name": "Player",
        "description": "A player",
        "max_hp": 10,
        "injury": 2,
        "health": "=player.max_hp - player.injury",
        "mood": "calm",
    }
    if extra_player_fields:
        player.update(extra_player_fields)
    entity_type: dict[str, object] = {
        "id": "Player",
        "name": "Player",
        "traits": ["described"],
        "entities": [player],
    }
    if instructions is not None:
        entity_type["instructions"] = instructions
    return {
        "id": "test/dyn-resolve",
        "source": ProjectSource.LOCAL,
        "title": "Test Project",
        "description": "A test project",
        "entity_types": [entity_type],
    }


def test_three_tier_precedence() -> None:
    project = Project.from_data(_player_project_data())
    context = StoryContext(project)

    # Static tier: plain project default
    assert context.get_field("player", "mood") == "calm"
    # Dynamic tier: expression evaluated against project defaults
    assert context.get_field("player", "health") == 8


def test_session_override_shadows_dynamic_expression_inputs() -> None:
    project = Project.from_data(_player_project_data())
    data = SessionStateData(entities={"player": {"injury": 5, "mood": "angry"}})
    context = StoryContext(project, data)

    # Override wins over the static default
    assert context.get_field("player", "mood") == "angry"
    # The override is visible to dynamic expressions (effective state)
    assert context.get_field("player", "health") == 5


def test_re_evaluation_after_state_change() -> None:
    project = Project.from_data(_player_project_data())
    context = StoryContext(project)

    assert context.get_field("player", "health") == 8
    context.session_state.set_field("player", "injury", 6)
    assert context.get_field("player", "health") == 4


def test_nested_dynamic_fields() -> None:
    data = {
        "id": "test/dyn-nested",
        "source": ProjectSource.LOCAL,
        "title": "Test Project",
        "description": "A test project",
        "entity_types": [
            {
                "id": "Player",
                "name": "Player",
                "traits": ["described"],
                "entities": [
                    {"id": "base", "name": "Base", "description": "Base", "v": 7},
                    {
                        "id": "b",
                        "name": "B",
                        "description": "B",
                        "y": "=base.v",
                    },
                    {
                        "id": "a",
                        "name": "A",
                        "description": "A",
                        "x": "=b.y",
                    },
                ],
            }
        ],
    }
    project = Project.from_data(data)
    context = StoryContext(project)

    assert context.get_field("a", "x") == 7
    context.session_state.set_field("base", "v", 9)
    assert context.get_field("a", "x") == 9


def test_context_exposes_read_only_fields() -> None:
    project = Project.from_data(_player_project_data())
    context = StoryContext(project)

    assert context.read_only_fields == {("player", "health")}
    assert context.session_state.read_only_fields == {("player", "health")}


def test_setting_dynamic_field_raises_read_only_error() -> None:
    project = Project.from_data(_player_project_data())
    context = StoryContext(project)

    with pytest.raises(DynamicFieldReadOnlyError, match="player\\.health"):
        context.session_state.set_field("player", "health", 99)


def test_guard_survives_dispatch_and_reset() -> None:
    project = Project.from_data(_player_project_data())
    context = StoryContext(project)

    # Cloning state through a dispatch keeps the read-only set intact
    context.store.dispatch(EndGameAction(reason="done"))
    with pytest.raises(DynamicFieldReadOnlyError, match="player\\.health"):
        context.session_state.set_field("player", "health", 99)

    # Reset clears overrides but keeps the guard, and the field re-evaluates
    context.store.dispatch(ResetGameAction())
    assert context.get_field("player", "health") == 8
    with pytest.raises(DynamicFieldReadOnlyError, match="player\\.health"):
        context.session_state.set_field("player", "health", 99)


def test_unguarded_session_state_unaffected() -> None:
    # A SessionState without the injection behaves exactly as before
    state = SessionState()

    state.set_field("player", "health", 99)

    assert state.get_field("player", "health") == 99
    assert state.read_only_fields == frozenset()


def test_dynamic_field_eval_error_names_field_and_source() -> None:
    project = Project.from_data(_player_project_data({"broken": "=player.nonexistent + 1"}))
    context = StoryContext(project)

    with pytest.raises(DynamicFieldEvalError) as excinfo:
        context.get_field("player", "broken")

    assert excinfo.value.field == "player.broken"
    assert excinfo.value.source == "=player.nonexistent + 1"
    message = str(excinfo.value)
    assert "player.broken" in message
    assert "=player.nonexistent + 1" in message


def test_missing_field_still_raises_entity_field_not_found() -> None:
    project = Project.from_data(_player_project_data())
    context = StoryContext(project)

    with pytest.raises(EntityFieldNotFoundError):
        context.get_field("player", "no_such_field")


def test_reducer_write_path_is_guarded() -> None:
    # Every state write goes through SessionState.set_field, so the guard
    # also covers reducer-driven writes (the graph transition reducer writes
    # `current_node_id` on the target entity).
    data = _player_project_data({"current_node_id": "=player.mood"})
    project = Project.from_data(data)
    context = StoryContext(project)

    action = GraphTransitionAction(entity_id="player", to="somewhere")
    with pytest.raises(DynamicFieldReadOnlyError, match="player\\.current_node_id"):
        context.store.dispatch(action)


def test_dynamic_field_on_read_only_property_fails_load() -> None:
    # `current_node_id` is a setter-less property on graph entities; it
    # cannot hold a dynamic definition, so load fails with a clear message.
    data = {
        "id": "test/dyn-property",
        "source": ProjectSource.LOCAL,
        "title": "Test Project",
        "description": "A test project",
        "entity_types": [
            {
                "id": "DynNode",
                "name": "Dyn Node",
                "traits": ["described", "graph_node"],
                "entities": [
                    {"id": "north", "name": "North", "description": "Node 1"},
                    {"id": "south", "name": "South", "description": "Node 2"},
                ],
            },
            {
                "id": "DynGraph",
                "name": "Dyn Graph",
                "traits": ["described", {"name": "graph", "node_type_id": "DynNode"}],
                "entities": [
                    {
                        "id": "map",
                        "name": "Map",
                        "description": "A map",
                        "node_ids": ["north", "south"],
                        "current_node_id": "=north.name",
                    }
                ],
            },
        ],
    }

    with pytest.raises(ValueError, match="cannot be a dynamic field"):
        Project.from_data(data)


def test_snapshot_has_no_dynamic_entries_and_restore_re_evaluates() -> None:
    project = Project.from_data(_player_project_data())
    context = StoryContext(project)

    assert context.get_field("player", "health") == 8
    initial_snapshot = context.session_state.data.model_dump()

    # A state change alters the effective (dynamic) value, but only the
    # stored field enters the snapshot
    context.session_state.set_field("player", "injury", 5)
    assert context.get_field("player", "health") == 5
    snapshot = context.session_state.data.model_dump()
    assert snapshot["entities"]["player"] == {"injury": 5}

    # Restore the historical snapshot (as CoreActionExecutor._restore does):
    # dynamic fields re-evaluate against the restored state
    restored = SessionState.from_json(
        SessionStateData.model_validate(initial_snapshot).model_dump_json(),
        read_only_fields=context.read_only_fields,
    )
    context.store.set_state(restored)

    assert context.get_field("player", "health") == 8
    with pytest.raises(DynamicFieldReadOnlyError, match="player\\.health"):
        context.session_state.set_field("player", "health", 99)


async def test_entity_view_resolves_dynamic_fields() -> None:
    project = Project.from_data(_player_project_data())
    context = StoryContext(project)
    view = EntityView(project.get_entity("player"), context)

    assert view.health == 8
    context.session_state.set_field("player", "injury", 5)
    assert view.health == 5

    # Static and session-overridden fields are unaffected
    assert view.mood == "calm"
    context.session_state.set_field("player", "mood", "angry")
    assert view.mood == "angry"


async def test_system_prompt_renders_dynamic_field_values() -> None:
    project = Project.from_data(
        _player_project_data({"description": "=player.max_hp"}, instructions="Player data.")
    )
    context = StoryContext(project)

    prompt = await context.get_system_prompt()

    assert "10" in prompt
    # Re-rendering after a state change picks up the new evaluated value
    context.session_state.set_field("player", "max_hp", 12)
    prompt = await context.get_system_prompt()
    assert "12" in prompt
