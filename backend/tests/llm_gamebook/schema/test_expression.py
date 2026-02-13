import pytest

from llm_gamebook.schema.expression import BoolExprDefinition
from llm_gamebook.story.conditions import bool_expr_grammar as g
from llm_gamebook.story.project import Project


def test_bool_expr_definition_parse_string() -> None:
    """Test parsing a string expression."""
    expr_def = BoolExprDefinition.model_validate("node_a.enabled")
    assert isinstance(expr_def.value, g.BoolExpr)
    assert isinstance(expr_def.value, g.DotPath)
    assert expr_def.value.entity_id.value == "node_a"
    assert len(expr_def.value.property_chain) == 1
    assert expr_def.value.property_chain[0].value == "enabled"


def test_bool_expr_definition_parse_list() -> None:
    """Test parsing a list of expressions (AND logic)."""
    expr_def = BoolExprDefinition.model_validate(["node_a.enabled", "node_b.enabled"])
    assert isinstance(expr_def.value, list)
    assert len(expr_def.value) == 2
    assert all(isinstance(expr, g.BoolExpr) for expr in expr_def.value)


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        # --- Literals (YAML native types) ---
        (True, True),
        (False, False),
        # --- Literals (String expressions) ---
        ("true", True),
        ("false", False),
        # --- DotPaths (referencing 'simple_project' state) ---
        ("node_a.enabled", True),
        ("node_b.enabled", False),
        # --- Comparisons (DotPath vs Literal) ---
        ("node_a.name == 'Node A'", True),
        ("node_a.name != 'Node B'", True),
        # --- Comparisons (Literal vs Literal) ---
        ("10 > 5", True),
        ("10 < 5", False),
        ("10 == 5", False),
        ("10 == 10", True),
        ("'foo' == 'foo'", True),
        # --- Boolean Logic (not, and, or) ---
        ("not node_a.enabled", False),
        ("not node_b.enabled", True),
        ("node_a.enabled and node_b.enabled", False),
        ("node_a.enabled or node_b.enabled", True),
        ("node_a.enabled and true", True),
        # --- Precedence ---
        ("node_a.enabled or node_b.enabled and false", True),  # 'and' binds tighter than 'or'
        ("not node_a.enabled or not node_b.enabled == 10", True),
        # --- Lists (Implicit AND) ---
        ([], True),
        ([5, True, False], False),
        ([5, True, True], True),
        # List of strings
        (["node_a.enabled", "node_b.enabled"], False),
        # Mixed types (String + Native Bool)
        (["node_a.enabled", True], True),
        (["node_a.enabled", False], False),
        # Nested logic in list
        (["node_a.enabled", "not node_b.enabled"], True),
    ],
)
def test_bool_expr_definition_evaluate_with_project(
    simple_project: Project, value: str, *, expected: bool
) -> None:
    expr_def = BoolExprDefinition.model_validate(value)
    result = expr_def.evaluate(simple_project)
    assert result is expected


@pytest.mark.parametrize(
    "value",
    [
        # --- Syntax Errors ---
        "node_a..enabled",  # Double dot
        ".enabled",  # Leading dot
        "node_a.",  # Trailing dot
        "node_a.enabled.",  # Trailing dot
        "node_a enabled",  # Missing operator
        "node_a.enabled ==",  # Incomplete comparison
        "== true",  # Missing left operand
        "node_a.count >> 5",  # Invalid operator
        # --- Keyword Errors ---
        "node_a and and node_b",  # Double operator
        "or node_a.enabled",  # Leading operator
        "node_a.enabled or",  # Trailing operator
        "notted node_a.enabled",  # Typo in keyword
        # --- Literal Errors ---
        "'unclosed string",  # Unclosed quote
        # --- Structure Errors ---
        "",  # Empty string
        {},
        {"foo": "bar"},
        [{}, 5],
        [5, True, []],
    ],
)
def test_bool_expr_definition_invalid_expression(value: str) -> None:
    with pytest.raises(ValueError, match="validation error"):
        BoolExprDefinition.model_validate(value)


def test_bool_expr_circular_reference() -> None:
    project = Project.from_data({
        "title": "Test Project",
        "description": "A test project",
        "entity_types": [
            {
                "id": "TestGraph",
                "name": "Test Graph",
                "traits": [
                    {"name": "graph", "node_type_id": "TestNode"},
                ],
                "entities": [
                    {
                        "id": "test_graph",
                        "name": "Test Graph",
                        "node_ids": ["some_node", "other_node"],
                        "current_node_id": "some_node",
                    }
                ],
            },
            {
                "id": "TestNode",
                "name": "Test Node",
                "traits": ["described", "graph_node"],
                "entities": [
                    {
                        "id": "some_node",
                        "name": "Some Node",
                        "description": "Just some node",
                        "enabled": "other_node.enabled",
                        "edge_ids": ["other_node"],
                    },
                    {
                        "id": "other_node",
                        "name": "Other Node",
                        "description": "Some other node",
                        "enabled": "some_node.enabled",
                        "edge_ids": ["some_node"],
                    },
                ],
            },
        ],
    })

    expr_def = BoolExprDefinition.model_validate("some_node.enabled")
    with pytest.raises(RecursionError, match="maximum recursion depth exceeded"):
        expr_def.evaluate(project)
