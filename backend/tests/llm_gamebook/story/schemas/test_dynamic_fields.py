"""Load-time behavior of dynamic (=`expression`) entity fields."""

import pytest

from llm_gamebook.story.schemas import BaseEntity, Project, ProjectSource, ValueExprDefinition
from llm_gamebook.story.schemas.project import (
    collect_dynamic_fields,
    detect_dynamic_field_cycles,
    iter_entity_field_values,
)


def _field(entity: BaseEntity, name: str) -> object:
    """Look up a field value (declared or extra) on an entity by name."""
    return next(v for n, v in iter_entity_field_values(entity) if n == name)


def _project_data(entities: list[dict[str, object]]) -> dict[str, object]:
    return {
        "id": "test/dyn-fields",
        "source": ProjectSource.LOCAL,
        "title": "Test Project",
        "description": "A test project",
        "entity_types": [
            {
                "id": "Player",
                "name": "Player",
                "traits": ["described"],
                "entities": entities,
            }
        ],
    }


# Dynamic field parsing at load


def test_dynamic_extra_attribute_is_parsed_at_load() -> None:
    project = Project.from_data(
        _project_data([
            {
                "id": "player",
                "name": "Player",
                "description": "A player",
                "health": "=player.max_hp - player.injury",
            }
        ])
    )

    entity = project.get_entity("player")
    health = _field(entity, "health")

    assert isinstance(health, ValueExprDefinition)
    assert health.source == "=player.max_hp - player.injury"
    # The AST is stored (an arithmetic expression, not a flat string)
    assert health.value is not None


def test_dynamic_trait_declared_field_is_parsed_at_load() -> None:
    # `description` is a str field declared by the `described` trait
    project = Project.from_data(
        _project_data([
            {
                "id": "player",
                "name": "Player",
                "description": "=player.mood",
                "mood": "restless",
            }
        ])
    )

    entity = project.get_entity("player")
    description = _field(entity, "description")

    assert isinstance(description, ValueExprDefinition)
    assert description.source == "=player.mood"
    # Sibling static fields are untouched
    assert _field(entity, "mood") == "restless"


def test_collect_dynamic_fields_maps_entity_and_field() -> None:
    project = Project.from_data(
        _project_data([
            {
                "id": "player",
                "name": "Player",
                "description": "A player",
                "health": "=player.max_hp - player.injury",
                "static": "value",
            }
        ])
    )

    assert set(collect_dynamic_fields(project)) == {("player", "health")}
    # iter_entity_field_values covers both declared and extra attributes
    values = dict(iter_entity_field_values(project.get_entity("player")))
    assert "health" in values
    assert "static" in values
    assert values["static"] == "value"


def test_static_strings_are_unchanged() -> None:
    project = Project.from_data(
        _project_data([
            {
                "id": "player",
                "name": "Player",
                "description": "A player",
                "mood": "restless",
            }
        ])
    )

    entity = project.get_entity("player")
    assert _field(entity, "mood") == "restless"
    assert collect_dynamic_fields(project) == {}


def test_value_expr_definition_str_returns_source() -> None:
    definition = ValueExprDefinition.model_validate("=player.max_hp - player.injury")
    assert str(definition) == "=player.max_hp - player.injury"


# Unparseable fields fail load


def test_unparseable_dynamic_field_fails_load_naming_entity_and_field() -> None:
    with pytest.raises(ValueError, match="Entity 'player' field 'health'"):
        Project.from_data(
            _project_data([
                {
                    "id": "player",
                    "name": "Player",
                    "description": "A player",
                    "health": "=player.max_hp player.injury",
                }
            ])
        )


# Circular dependencies are rejected at load


def test_self_cycle_fails_load_naming_the_cycle() -> None:
    with pytest.raises(ValueError, match="Circular dynamic field dependency"):
        Project.from_data(
            _project_data([
                {
                    "id": "player",
                    "name": "Player",
                    "description": "A player",
                    "x": "=player.x + 1",
                }
            ])
        )


def test_indirect_cycle_fails_load_naming_the_path() -> None:
    data = _project_data([
        {
            "id": "a",
            "name": "A",
            "description": "Entity A",
            "x": "=b.y",
        },
        {
            "id": "b",
            "name": "B",
            "description": "Entity B",
            "y": "=a.x",
        },
    ])

    with pytest.raises(ValueError, match="a\\.x \u2192 b\\.y \u2192 a\\.x"):
        Project.from_data(data)


def test_diamond_dependency_loads() -> None:
    data = _project_data([
        {
            "id": "base",
            "name": "Base",
            "description": "Entity Base",
            "v": 5,
        },
        {
            "id": "a",
            "name": "A",
            "description": "Entity A",
            "x": "=base.v",
        },
        {
            "id": "b",
            "name": "B",
            "description": "Entity B",
            "y": "=base.v",
        },
    ])

    project = Project.from_data(data)
    assert set(collect_dynamic_fields(project)) == {("a", "x"), ("b", "y")}
    # No cycle: calling the detector again is a no-op
    detect_dynamic_field_cycles(project)


def test_deeper_chain_references_do_not_create_cycles() -> None:
    # The head of `other.items.count` is `other.items` (static); the deeper
    # `count` property cannot be dynamic-recursive.
    data = _project_data([
        {
            "id": "other",
            "name": "Other",
            "description": "Entity Other",
            "items": [],
        },
        {
            "id": "a",
            "name": "A",
            "description": "Entity A",
            "x": "=other.items.count",
        },
    ])

    project = Project.from_data(data)
    assert set(collect_dynamic_fields(project)) == {("a", "x")}


# Legacy projects without `=` fields load identically


def test_legacy_project_without_dynamic_fields_loads() -> None:
    data = _project_data([
        {
            "id": "player",
            "name": "Player",
            "description": "A player",
            "mood": "restless",
            "hp": 10,
        }
    ])

    project = Project.from_data(data)
    entity = project.get_entity("player")
    assert _field(entity, "mood") == "restless"
    assert _field(entity, "hp") == 10
    assert collect_dynamic_fields(project) == {}
