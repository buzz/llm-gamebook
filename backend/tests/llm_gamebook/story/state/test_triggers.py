"""Tests for the trigger system (Stage 4)."""

import logging
from typing import cast

import pytest
from pydantic import BaseModel

from llm_gamebook.story.context import StoryContext
from llm_gamebook.story.errors import ExpressionEvalError
from llm_gamebook.story.schemas import Project, ProjectSource, TriggerDefinition
from llm_gamebook.story.state import Action, Reducer, SessionState, is_trigger_condition_true
from llm_gamebook.story.traits.graph import GraphTransitionAction


def trigger_project_data(triggers: list[dict[str, object]] | None = None) -> dict[str, object]:
    entity_types: list[dict[str, object]] = [
        {
            "id": "MainGraph",
            "name": "Main Graph",
            "traits": ["described", {"name": "graph", "node_type_id": "MainNode"}],
            "entities": [
                {
                    "id": "main",
                    "name": "Main",
                    "description": "Main story arc",
                    "node_ids": ["start", "middle", "end"],
                    "current_node_id": "start",
                }
            ],
        },
        {
            "id": "MainNode",
            "name": "Main Node",
            "traits": ["described", "graph_node"],
            "entities": [
                {"id": "start", "name": "Start", "description": "Start", "edge_ids": ["middle"]},
                {"id": "middle", "name": "Middle", "description": "Middle", "edge_ids": ["end"]},
                {"id": "end", "name": "End", "description": "End", "edge_ids": []},
            ],
        },
    ]
    if triggers is not None:
        entity_types[0]["triggers"] = triggers
    return {
        "id": "llm-gamebook/trigger-test",
        "source": ProjectSource.LOCAL,
        "title": "Trigger Test",
        "description": "A project with triggers",
        "entity_types": entity_types,
    }


def make_context(triggers: list[dict[str, object]] | None = None) -> StoryContext:
    return StoryContext(Project.from_data(trigger_project_data(triggers)))


def make_flag_reducer(log: list[str], field: str = "flag") -> Reducer:
    def reducer(state: SessionState, action: Action[BaseModel]) -> SessionState:
        log.append(action.name)
        data = action.payload.model_dump()
        entity_id = data.get("entity_id")
        value = data.get("value")
        if isinstance(entity_id, str) and isinstance(value, str | int | bool | float):
            state.set_field(entity_id, field, value)
        return state

    return reducer


def dispatch_transition(context: StoryContext, to: str) -> None:
    """Dispatch a graph transition, as the LLM transition tool does."""
    context.store.dispatch(GraphTransitionAction(entity_id="main", to=to))


class NoopPayload(BaseModel):
    """Empty payload for ad-hoc actions (e.g. testing)."""


@pytest.fixture
def trigger_context() -> StoryContext:
    return make_context()


def test_entity_type_loads_triggers_in_yaml_order() -> None:
    context = make_context([
        {"name": "test/second", "condition": "main.current_node_id == 'end'", "args": {}},
        {"name": "test/first", "condition": "main.current_node_id == 'end'", "args": {}},
    ])

    entity_type = context.project.get_entity_type("MainGraph")

    assert [t.name for t in entity_type.get_triggers()] == ["test/second", "test/first"]
    assert entity_type.triggers == entity_type.get_triggers()


def test_entity_type_triggers_default_empty(trigger_context: StoryContext) -> None:
    entity_type = trigger_context.project.get_entity_type("MainGraph")
    assert entity_type.get_triggers() == []


def test_condition_false_by_default(trigger_context: StoryContext) -> None:
    trigger = TriggerDefinition(name="test/flag", condition="main.current_node_id == 'end'")
    assert is_trigger_condition_true(trigger_context, trigger) is False


def test_condition_uses_session_override(trigger_context: StoryContext) -> None:
    trigger = TriggerDefinition(name="test/flag", condition="main.current_node_id == 'middle'")
    assert is_trigger_condition_true(trigger_context, trigger) is False

    trigger_context.session_state.set_field("main", "current_node_id", "middle")
    assert is_trigger_condition_true(trigger_context, trigger) is True


def test_condition_dynamic_prefix_is_equivalent(trigger_context: StoryContext) -> None:
    plain = TriggerDefinition(name="test/flag", condition="main.current_node_id == 'start'")
    dynamic = TriggerDefinition(name="test/flag", condition="=main.current_node_id == 'start'")
    assert is_trigger_condition_true(trigger_context, plain) is True
    assert is_trigger_condition_true(trigger_context, dynamic) is True


def test_middleware_dispatches_fired_trigger() -> None:
    log: list[str] = []
    context = make_context([
        {
            "name": "test/flag",
            "condition": "main.current_node_id == 'end'",
            "args": {"entity_id": "main", "value": "flagged"},
        }
    ])
    context.store._register_reducer("test/flag", make_flag_reducer(log))

    dispatch_transition(context, "middle")
    assert log == []
    assert context.session_state.get_field("main", "current_node_id") == "middle"

    dispatch_transition(context, "end")
    assert log == ["test/flag"]
    assert context.session_state.get_field("main", "flag") == "flagged"


def test_multiple_triggers_fire_in_yaml_order() -> None:
    log: list[str] = []
    context = make_context([
        {"name": "test/flag_b", "condition": "main.current_node_id == 'end'", "args": {}},
        {"name": "test/flag_a", "condition": "main.current_node_id == 'end'", "args": {}},
    ])
    context.store._register_reducer("test/flag_b", make_flag_reducer(log, "flag_b"))
    context.store._register_reducer("test/flag_a", make_flag_reducer(log, "flag_a"))

    dispatch_transition(context, "end")

    assert log == ["test/flag_b", "test/flag_a"]


def test_trigger_chaining_in_same_step() -> None:
    # test/flag_a fires on reaching 'end'; its state change enables test/flag_b,
    # which fires within the same step.
    log: list[str] = []
    context = make_context([
        {
            "name": "test/flag_a",
            "condition": "main.current_node_id == 'end'",
            "args": {"entity_id": "main", "value": "a"},
        },
        {
            "name": "test/flag_b",
            "condition": "main.flag_a == 'a'",
            "args": {"entity_id": "main", "value": "b"},
        },
    ])
    context.store._register_reducer("test/flag_a", make_flag_reducer(log, "flag_a"))
    context.store._register_reducer("test/flag_b", make_flag_reducer(log, "flag_b"))

    dispatch_transition(context, "end")

    assert log == ["test/flag_a", "test/flag_b"]
    assert context.session_state.get_field("main", "flag_a") == "a"
    assert context.session_state.get_field("main", "flag_b") == "b"


def test_loop_prevention_skips_same_action_type() -> None:
    # Trigger dispatches the same action type as the user action just executed: skipped.
    context = make_context([
        {
            "name": "graph/transition",
            "condition": "main.current_node_id == 'end'",
            "args": {"entity_id": "main", "to": "middle"},
        }
    ])

    dispatch_transition(context, "end")

    assert context.session_state.get_field("main", "current_node_id") == "end"


def test_loop_prevention_is_cumulative_across_nested_dispatches() -> None:
    log: list[str] = []
    context = make_context([
        {
            "name": "test/flag",
            "condition": "main.current_node_id == 'end'",
            "args": {"entity_id": "main", "value": "flagged"},
        },
        {
            "name": "graph/transition",
            "condition": "main.current_node_id == 'end'",
            "args": {"entity_id": "main", "to": "middle"},
        },
    ])
    context.store._register_reducer("test/flag", make_flag_reducer(log))

    dispatch_transition(context, "end")

    assert log == ["test/flag"]
    # The graph/transition trigger must not re-dispatch: the user action type
    # is tracked across the nested trigger dispatch.
    assert context.session_state.get_field("main", "current_node_id") == "end"


def test_invalid_condition_raises_on_evaluation() -> None:
    context = make_context()
    bad_trigger = TriggerDefinition.model_construct(
        name="test/flag", condition="this is !!! not valid", args={}
    )
    context.project.get_entity_type("MainGraph").triggers = [bad_trigger]

    with pytest.raises(ExpressionEvalError, match="Invalid trigger condition"):
        dispatch_transition(context, "middle")


def test_missing_entity_in_condition_raises() -> None:
    context = make_context()
    trigger = TriggerDefinition.model_construct(
        name="test/flag", condition="ghost.current_node_id == 'x'", args={}
    )
    context.project.get_entity_type("MainGraph").triggers = [trigger]

    with pytest.raises(ExpressionEvalError, match="Invalid entity ID: ghost"):
        dispatch_transition(context, "middle")


def test_trigger_evaluation_is_logged(caplog: pytest.LogCaptureFixture) -> None:
    context = make_context([
        {
            "name": "test/flag",
            "condition": "main.current_node_id == 'end'",
            "args": {},
        }
    ])

    with caplog.at_level(logging.INFO, logger="llm_gamebook.story.state.triggers"):
        dispatch_transition(context, "end")

    assert any(
        "Trigger fired: dispatching 'test/flag'" in record.message for record in caplog.records
    )


def test_trigger_condition_reads_dynamic_field() -> None:
    # A trigger condition referencing a dynamic field is evaluated
    # transparently against the current effective state.
    data = trigger_project_data([
        {
            "name": "test/flag",
            "condition": "main.at_end",
            "args": {"entity_id": "main", "value": "flagged"},
        }
    ])
    entity_types = cast("list[dict[str, object]]", data["entity_types"])
    main_entities = cast("list[dict[str, object]]", entity_types[0]["entities"])
    main = main_entities[0]
    main["at_end"] = "=main.current_node_id == 'end'"

    context = StoryContext(Project.from_data(data))
    log: list[str] = []
    context.store._register_reducer("test/flag", make_flag_reducer(log))

    assert context.get_field("main", "at_end") is False
    dispatch_transition(context, "middle")
    assert log == []

    dispatch_transition(context, "end")
    assert log == ["test/flag"]
    assert context.session_state.get_field("main", "flag") == "flagged"


def test_integration_full_trigger_flow() -> None:
    log: list[str] = []
    context = make_context([
        {
            "name": "test/flag",
            "condition": "=main.current_node_id == 'end'",
            "args": {"entity_id": "main", "value": "flagged"},
        }
    ])
    context.store._register_reducer("test/flag", make_flag_reducer(log))

    # Simulate the LLM transition tool: dispatch a graph/transition action.
    dispatch_transition(context, "end")

    state = context.session_state
    assert state.get_field("main", "current_node_id") == "end"
    assert state.get_field("main", "flag") == "flagged"
    assert log == ["test/flag"]

    # Triggers re-evaluate on every dispatch (no once-only semantics in Stage 4).
    context.store.dispatch(Action[NoopPayload](name="test/noop", payload=NoopPayload()))
    assert log == ["test/flag", "test/flag"]
