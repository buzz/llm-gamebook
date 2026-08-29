from typing import TYPE_CHECKING, cast

import pytest
from pydantic import BaseModel

from llm_gamebook.story.conditions import bool_expr_grammar as g
from llm_gamebook.story.conditions.evaluator import MAX_EVAL_DEPTH, BoolExprEvaluator
from llm_gamebook.story.conditions.grammar import ComparisonOperatorValue
from llm_gamebook.story.errors import DynamicFieldEvalError, ExpressionEvalError

if TYPE_CHECKING:
    from llm_gamebook.story.traits.described import DescribedTrait


def test_bool_expr_evaluator_eval_literal_true(evaluator: BoolExprEvaluator) -> None:
    expr = g.BoolLiteral(value=True)
    result = evaluator.eval(expr)
    assert result is True


def test_bool_expr_evaluator_eval_literal_false(evaluator: BoolExprEvaluator) -> None:
    expr = g.BoolLiteral(value=False)
    result = evaluator.eval(expr)
    assert result is False


def test_bool_expr_evaluator_eval_dot_path(evaluator: BoolExprEvaluator) -> None:
    expr = g.DotPath(
        entity_id=g.SnakeCase(value="node_a"),
        property_chain=(g.SnakeCase(value="name"),),
    )
    result = evaluator.eval(expr)
    assert result is True


def test_bool_expr_evaluator_eval_comparison_equal(evaluator: BoolExprEvaluator) -> None:
    left = g.DotPath(
        entity_id=g.SnakeCase(value="node_a"),
        property_chain=(g.SnakeCase(value="name"),),
    )
    right = g.StrLiteral(value="Node A")
    op = g.ComparisonOperator(value="==")
    expr = g.Comparison(left=left, op=op, right=right)
    result = evaluator.eval(expr)
    assert result is True


def test_bool_expr_evaluator_eval_comparison_not_equal(evaluator: BoolExprEvaluator) -> None:
    left = g.DotPath(
        entity_id=g.SnakeCase(value="node_a"),
        property_chain=(g.SnakeCase(value="name"),),
    )
    right = g.StrLiteral(value="Node B")
    op = g.ComparisonOperator(value="!=")
    expr = g.Comparison(left=left, op=op, right=right)
    result = evaluator.eval(expr)
    assert result is True


def test_bool_expr_evaluator_eval_comparison_less(evaluator: BoolExprEvaluator) -> None:
    left = g.IntLiteral(value=5)
    right = g.IntLiteral(value=10)
    op = g.ComparisonOperator(value="<")
    expr = g.Comparison(left=left, op=op, right=right)
    result = evaluator.eval(expr)
    assert result is True


def test_bool_expr_evaluator_eval_comparison_greater(evaluator: BoolExprEvaluator) -> None:
    left = g.IntLiteral(value=10)
    right = g.IntLiteral(value=5)
    op = g.ComparisonOperator(value=">")
    expr = g.Comparison(left=left, op=op, right=right)
    result = evaluator.eval(expr)
    assert result is True


def test_bool_expr_evaluator_eval_comparison_less_equal(evaluator: BoolExprEvaluator) -> None:
    left = g.IntLiteral(value=5)
    right = g.IntLiteral(value=5)
    op = g.ComparisonOperator(value="<=")
    expr = g.Comparison(left=left, op=op, right=right)
    result = evaluator.eval(expr)
    assert result is True


def test_bool_expr_evaluator_eval_comparison_greater_equal(evaluator: BoolExprEvaluator) -> None:
    left = g.IntLiteral(value=10)
    right = g.IntLiteral(value=5)
    op = g.ComparisonOperator(value=">=")
    expr = g.Comparison(left=left, op=op, right=right)
    result = evaluator.eval(expr)
    assert result is True


def test_bool_expr_evaluator_eval_and(evaluator: BoolExprEvaluator) -> None:
    left = g.BoolLiteral(value=True)
    right = g.BoolLiteral(value=False)
    expr = g.AndExpr(left=left, right=right)
    result = evaluator.eval(expr)
    assert result is False


def test_bool_expr_evaluator_eval_or(evaluator: BoolExprEvaluator) -> None:
    left = g.BoolLiteral(value=True)
    right = g.BoolLiteral(value=False)
    expr = g.OrExpr(left=left, right=right)
    result = evaluator.eval(expr)
    assert result is True


def test_bool_expr_evaluator_eval_not(evaluator: BoolExprEvaluator) -> None:
    expr = g.NotExpr(expr=g.BoolLiteral(value=True))
    result = evaluator.eval(expr)
    assert result is False


def test_bool_expr_evaluator_resolve_dot_path(evaluator: BoolExprEvaluator) -> None:
    dot_path = g.DotPath(
        entity_id=g.SnakeCase(value="test_graph"),
        property_chain=(g.SnakeCase(value="current_node_id"),),
    )
    result = evaluator._resolve_dot_path(dot_path)
    assert cast("str", result) == "node_a"


def test_bool_expr_evaluator_resolve_entity(evaluator: BoolExprEvaluator) -> None:
    entity = evaluator._resolve_entity("node_a")
    assert entity.id == "node_a"
    described_entity = cast("DescribedTrait", entity)
    assert described_entity.name == "Node A"


def test_bool_expr_evaluator_resolve_entity_property(evaluator: BoolExprEvaluator) -> None:
    entity = evaluator._resolve_entity("node_a")
    result = evaluator._resolve_entity_property(entity, "name")
    assert result == "Node A"


def test_bool_expr_evaluator_comparison_unsupported_left(evaluator: BoolExprEvaluator) -> None:
    dot_path = g.DotPath(
        entity_id=g.SnakeCase(value="test_graph"),
        property_chain=(g.SnakeCase(value="nonexistent_property"),),
    )
    left = dot_path
    right = g.StrLiteral(value="test")
    op = g.ComparisonOperator(value="==")
    expr = g.Comparison(left=left, op=op, right=right)
    with pytest.raises(ExpressionEvalError):
        evaluator.eval(expr)


def test_bool_expr_evaluator_comparison_unsupported_right(evaluator: BoolExprEvaluator) -> None:
    left = g.StrLiteral(value="test")
    dot_path = g.DotPath(
        entity_id=g.SnakeCase(value="test_graph"),
        property_chain=(g.SnakeCase(value="nonexistent_property"),),
    )
    right = dot_path
    op = g.ComparisonOperator(value="==")
    expr = g.Comparison(left=left, op=op, right=right)
    with pytest.raises(ExpressionEvalError):
        evaluator.eval(expr)


def test_bool_expr_evaluator_expression_eval_error(evaluator: BoolExprEvaluator) -> None:
    dot_path = g.DotPath(
        entity_id=g.SnakeCase(value="nonexistent_entity"),
        property_chain=(g.SnakeCase(value="name"),),
    )
    expr = g.NotExpr(expr=dot_path)
    with pytest.raises(ExpressionEvalError):
        evaluator.eval(expr)


def test_bool_expr_evaluator_eval_mid_chain_type_error(evaluator: BoolExprEvaluator) -> None:
    # Testing the mid-chain validation: test_graph.node_ids.something
    # node_ids is a Sequence[str], not a BaseEntity.
    # Because it is in the middle of the chain, it should trigger the error.
    dot_path = g.DotPath(
        entity_id=g.SnakeCase(value="test_graph"),
        property_chain=(
            g.SnakeCase(value="node_ids"),  # The 'mid-chain' item
            g.SnakeCase(value="id"),  # The 'final' item
        ),
    )

    with pytest.raises(
        ExpressionEvalError, match="Expected property node_ids on entity test_graph to be an entity"
    ):
        evaluator.eval(dot_path)


def test_bool_expr_evaluator_eval_comparison_invalid_types_on_inequality(
    evaluator: BoolExprEvaluator,
) -> None:
    # Testing that using < on a string vs int raises a standard Python TypeError
    # (since evaluator.py doesn't catch generic TypeErrors, only specific Entity/Sequence ones)
    left = g.StrLiteral(value="10")
    right = g.IntLiteral(value=5)
    comp = g.Comparison(left=left, op=g.ComparisonOperator(value="<"), right=right)

    with pytest.raises(TypeError):
        evaluator.eval(comp)


def test_bool_expr_evaluator_and_expr_evaluation_order(evaluator: BoolExprEvaluator) -> None:
    # Ensure nested logic works: (True and True) and False
    expr = g.AndExpr(
        left=g.AndExpr(left=g.BoolLiteral(value=True), right=g.BoolLiteral(value=True)),
        right=g.BoolLiteral(value=False),
    )
    assert evaluator.eval(expr) is False


def test_bool_expr_evaluator_comparison_type_error_on_entities(
    evaluator: BoolExprEvaluator,
) -> None:
    # Comparisons like <, <=, >, >= should fail if operands are entities or sequences
    comp = g.Comparison(
        left=g.IntLiteral(value=10),
        op=g.ComparisonOperator(value="<"),
        right=g.DotPath(
            entity_id=g.SnakeCase(value="node_a"), property_chain=(g.SnakeCase(value="edge_ids"),)
        ),
    )
    # edge_ids is a Sequence. Comparison < should raise TypeError.
    with pytest.raises(TypeError, match="not supported for comparison"):
        evaluator.eval(comp)


def test_bool_expr_evaluator_logical_short_circuit(evaluator: BoolExprEvaluator) -> None:
    # AND short-circuit: False and (Error) -> False
    left = g.BoolLiteral(value=False)
    right = g.DotPath(
        entity_id=g.SnakeCase(value="nonexistent"), property_chain=(g.SnakeCase(value="any"),)
    )
    expr_and = g.AndExpr(left=left, right=right)
    assert evaluator.eval(expr_and) is False

    # OR short-circuit: True or (Error) -> True
    left_or = g.BoolLiteral(value=True)
    expr_or = g.OrExpr(left=left_or, right=right)
    assert evaluator.eval(expr_or) is True


@pytest.mark.parametrize(
    ("left_val", "right_prop", "expected"),
    [
        ("node_b", "edge_ids", True),  # Success: item is in list
        ("node_c", "edge_ids", False),  # Failure: item not in list
        ("Node", "name", True),  # Success: substring in string
        ("Ghost", "name", False),  # Failure: substring not in string
    ],
)
def test_bool_expr_evaluator_eval_in_operator(
    evaluator: BoolExprEvaluator, left_val: str, right_prop: str, *, expected: bool
) -> None:
    left = g.StrLiteral(value=left_val)
    right = g.DotPath(
        entity_id=g.SnakeCase(value="node_a"),
        property_chain=(g.SnakeCase(value=right_prop),),
    )
    expr = g.Comparison(left=left, op=g.ComparisonOperator(value="in"), right=right)

    assert evaluator.eval(expr) is expected


def test_bool_expr_evaluator_in_operator_type_error(evaluator: BoolExprEvaluator) -> None:
    # Test 'in' where the right side is an integer (not a collection)
    # Using node_a.enabled which we'll assume returns a bool/int in this context
    left = g.IntLiteral(value=1)
    right = g.BoolLiteral(value=True)  # Non-collection

    expr = g.Comparison(left=left, op=g.ComparisonOperator(value="in"), right=right)

    with pytest.raises(TypeError, match="requires a collection"):
        evaluator.eval(expr)


def test_bool_expr_evaluator_in_operator_with_literals(evaluator: BoolExprEvaluator) -> None:
    # Testing 'in' with literal values (if the grammar supports it)
    # Logic check: 5 in [1, 5, 10]
    # Note: This assumes your resolve_comparison_operand can handle literal lists
    # if they exist in your grammar; otherwise, use dot-paths.
    left = g.IntLiteral(value=5)
    # If your grammar doesn't have ListLiteral, we use a dot_path to a sequence
    right = g.DotPath(
        entity_id=g.SnakeCase(value="test_graph"),
        property_chain=(g.SnakeCase(value="node_ids"),),
    )
    expr = g.Comparison(left=left, op=g.ComparisonOperator(value="in"), right=right)
    # test_graph.node_ids is ["node_a", "node_b"], so 5 should be False
    assert evaluator.eval(expr) is False


def test_bool_expr_evaluator_resolve_entity_not_found(evaluator: BoolExprEvaluator) -> None:
    with pytest.raises(ExpressionEvalError, match="Invalid entity ID: ghost_id"):
        evaluator._resolve_entity("ghost_id")


def test_bool_expr_evaluator_property_not_found(evaluator: BoolExprEvaluator) -> None:
    entity = evaluator._resolve_entity("node_a")
    with pytest.raises(ExpressionEvalError, match="Property 'mana' not found on entity 'node_a'"):
        evaluator._resolve_entity_property(entity, "mana")


@pytest.mark.parametrize(
    ("op", "left", "right", "expected"),
    [
        ("==", 10, 10, True),
        ("!=", 10, 5, True),
        ("<=", 5, 10, True),
        ("<=", 10, 10, True),
        (">=", 15, 10, True),
        (">=", 10, 10, True),
    ],
)
def test_bool_expr_evaluator_all_operators(
    evaluator: BoolExprEvaluator,
    op: ComparisonOperatorValue,
    left: int,
    right: int,
    *,
    expected: bool,
) -> None:
    expr = g.Comparison(
        left=g.IntLiteral(value=left),
        op=g.ComparisonOperator(value=op),
        right=g.IntLiteral(value=right),
    )
    assert evaluator.eval(expr) == expected


# Value evaluation (eval_value)
def test_eval_value_literals(evaluator: BoolExprEvaluator) -> None:
    assert evaluator.eval_value(g.IntLiteral(7)) == 7
    assert evaluator.eval_value(g.FloatLiteral(1.5)) == 1.5
    assert evaluator.eval_value(g.StrLiteral("hello")) == "hello"
    assert evaluator.eval_value(g.BoolLiteral(value=True)) is True
    assert evaluator.eval_value(g.BoolLiteral(value=False)) is False


def test_eval_value_dot_path(evaluator: BoolExprEvaluator) -> None:
    expr = g.DotPath(
        entity_id=g.SnakeCase(value="node_a"),
        property_chain=(g.SnakeCase(value="name"),),
    )
    assert evaluator.eval_value(expr) == "Node A"


def test_eval_value_dot_path_stored_bool_expr_is_returned_as_is(
    evaluator: BoolExprEvaluator,
) -> None:
    # Value context does not evaluate a stored BoolExprDefinition (design D5)
    expr = g.DotPath(
        entity_id=g.SnakeCase(value="node_b"),
        property_chain=(g.SnakeCase(value="enabled"),),
    )
    assert isinstance(evaluator.eval_value(expr), BaseModel)


def test_eval_value_comparison_is_boolean(evaluator: BoolExprEvaluator) -> None:
    comp = g.Comparison(
        left=g.DotPath(g.SnakeCase(value="node_a"), (g.SnakeCase(value="name"),)),
        op=g.ComparisonOperator(value="=="),
        right=g.StrLiteral(value="Node A"),
    )
    assert evaluator.eval_value(comp) is True

    comp_false = g.Comparison(
        left=g.DotPath(g.SnakeCase(value="node_a"), (g.SnakeCase(value="name"),)),
        op=g.ComparisonOperator(value="=="),
        right=g.StrLiteral(value="Node B"),
    )
    assert evaluator.eval_value(comp_false) is False


def test_eval_value_boolean_combinators(evaluator: BoolExprEvaluator) -> None:
    and_expr = g.AndExpr(left=g.BoolLiteral(value=True), right=g.BoolLiteral(value=False))
    assert evaluator.eval_value(and_expr) is False

    or_expr = g.OrExpr(left=g.BoolLiteral(value=True), right=g.BoolLiteral(value=False))
    assert evaluator.eval_value(or_expr) is True

    not_expr = g.NotExpr(expr=g.BoolLiteral(value=True))
    assert evaluator.eval_value(not_expr) is False


# Arithmetic (design D2 type rules)
def _arith(op: g.ArithOperatorValue, left: g.Expr, right: g.Expr) -> g.ArithExpr:
    return g.ArithExpr(left=left, operator=g.ArithOperator(op), right=right)


@pytest.mark.parametrize(
    ("left", "op", "right", "expected", "expected_type"),
    [
        (g.IntLiteral(3), "+", g.IntLiteral(4), 7, int),
        (g.IntLiteral(10), "-", g.IntLiteral(4), 6, int),
        (g.IntLiteral(3), "*", g.IntLiteral(4), 12, int),
        (g.IntLiteral(7), "/", g.IntLiteral(2), 3.5, float),
        (g.FloatLiteral(1.5), "+", g.IntLiteral(1), 2.5, float),
        (g.IntLiteral(3), "+", g.FloatLiteral(0.5), 3.5, float),
        (g.IntLiteral(7), "/", g.IntLiteral(4), 1.75, float),
        (g.IntLiteral(2), "-", g.IntLiteral(5), -3, int),
    ],
)
def test_eval_value_arith_type_rules(
    evaluator: BoolExprEvaluator,
    left: g.Expr,
    op: g.ArithOperatorValue,
    right: g.Expr,
    expected: float,
    expected_type: type[int] | type[float],
) -> None:
    result = evaluator.eval_value(_arith(op, left, right))
    assert result == expected
    assert type(result) is expected_type


@pytest.mark.parametrize(
    ("left", "op"),
    [
        (g.StrLiteral("player"), "+"),
        (g.BoolLiteral(value=True), "+"),
        (
            g.DotPath(
                entity_id=g.SnakeCase(value="test_graph"),
                property_chain=(g.SnakeCase(value="node_ids"),),
            ),
            "+",
        ),
    ],
)
def test_eval_value_arith_non_numeric_operand_is_error(
    evaluator: BoolExprEvaluator,
    left: g.Expr,
    op: g.ArithOperatorValue,
) -> None:
    expr = _arith(op, left, g.IntLiteral(1))
    with pytest.raises(ExpressionEvalError, match="requires numeric operands"):
        evaluator.eval_value(expr)


def test_eval_value_arith_nested(evaluator: BoolExprEvaluator) -> None:
    # ((2 + 3) * 4) / 2 == 10.0
    expr = _arith(
        "/",
        _arith("*", _arith("+", g.IntLiteral(2), g.IntLiteral(3)), g.IntLiteral(4)),
        g.IntLiteral(2),
    )
    result = evaluator.eval_value(expr)
    assert result == 10.0
    assert type(result) is float


def test_eval_arith_zero_division_is_error(evaluator: BoolExprEvaluator) -> None:
    expr = _arith("/", g.IntLiteral(1), g.IntLiteral(0))
    with pytest.raises(ZeroDivisionError):
        evaluator.eval_value(expr)


def test_eval_arith_expr_as_condition(evaluator: BoolExprEvaluator) -> None:
    # `2 + 3 > 4` parses and evaluates as a boolean condition
    expr = g.parse_bool_expr("2 + 3 > 4")
    assert evaluator.eval(expr) is True

    expr = g.parse_bool_expr("2 + 2 > 4")
    assert evaluator.eval(expr) is False


# Evaluation depth cap
def test_eval_value_depth_cap(evaluator: BoolExprEvaluator) -> None:
    evaluator._depth = MAX_EVAL_DEPTH
    with pytest.raises(DynamicFieldEvalError, match="Maximum expression evaluation depth"):
        evaluator.eval_value(g.IntLiteral(1))


def test_eval_value_depth_is_restored(evaluator: BoolExprEvaluator) -> None:
    evaluator.eval_value(g.IntLiteral(1))
    assert evaluator._depth == 0

    with pytest.raises(ExpressionEvalError):
        evaluator.eval_value(
            g.DotPath(
                entity_id=g.SnakeCase(value="nonexistent"),
                property_chain=(g.SnakeCase(value="any"),),
            )
        )
    assert evaluator._depth == 0
