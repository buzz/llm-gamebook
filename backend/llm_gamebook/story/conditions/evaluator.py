from collections.abc import Sequence
from contextlib import suppress
from typing import TYPE_CHECKING, assert_never, cast

from pydantic import BaseModel

from llm_gamebook.story.conditions import bool_expr_grammar as g
from llm_gamebook.story.errors import (
    DynamicFieldEvalError,
    EntityFieldNotFoundError,
    EntityNotFoundError,
    ExpressionEvalError,
)
from llm_gamebook.story.schemas.entity import BaseEntity, EntityProperty

if TYPE_CHECKING:
    from llm_gamebook.story.context import StoryContext
    from llm_gamebook.story.schemas.expression import BoolExprDefinition
    from llm_gamebook.story.schemas.project import Project


MAX_EVAL_DEPTH = 32
"""Runtime backstop for nested dynamic field evaluation depth.

Static cycle detection (at project load) makes this unreachable in practice;
it guards against future grammar features that make dependencies dynamic
(cf. the store's MAX_DISPATCH_DEPTH).
"""


class BoolExprEvaluator:
    def __init__(self, project: "Project", story_context: "StoryContext | None" = None) -> None:
        self._project = project
        self._story_context = story_context
        self._depth = 0

    def eval(self, expr: g.BoolExpr) -> bool:
        if isinstance(expr, g.Literal):
            return bool(expr.value)
        if isinstance(expr, g.DotPath):
            return self._eval_dot_path(expr)
        if isinstance(expr, g.Comparison):
            return self._eval_comparison(expr)
        if isinstance(expr, g.ArithExpr):
            return bool(self.eval_value(expr))
        if isinstance(expr, g.AndExpr):
            return self.eval(expr.left) and self.eval(expr.right)
        if isinstance(expr, g.OrExpr):
            return self.eval(expr.left) or self.eval(expr.right)
        if isinstance(expr, g.NotExpr):
            return not self.eval(expr.expr)

        assert_never(expr)

    def eval_value(self, expr: g.Expr) -> EntityProperty:
        """Evaluate a value expression to a field value.

        Dot paths and literals resolve to their (effective) values,
        comparisons evaluate to a boolean, arithmetic applies the numeric
        type rules, and boolean combinators evaluate to a boolean.

        Args:
            expr: The parsed value expression AST.

        Returns:
            The evaluated field value.

        Raises:
            ExpressionEvalError: If a reference or operand cannot be resolved.
            DynamicFieldEvalError: If the evaluation depth cap is exceeded.
        """
        if self._depth >= MAX_EVAL_DEPTH:
            msg = f"Maximum expression evaluation depth ({MAX_EVAL_DEPTH}) exceeded"
            raise DynamicFieldEvalError(msg)
        self._depth += 1
        try:
            if isinstance(expr, g.Literal):
                return expr.value
            if isinstance(expr, g.DotPath):
                return self._resolve_dot_path(expr)
            if isinstance(expr, g.ArithExpr):
                return self._eval_arith(expr)
            if isinstance(expr, g.Comparison):
                return self._eval_comparison(expr)
            if isinstance(expr, g.AndExpr):
                return self.eval(expr.left) and self.eval(expr.right)
            if isinstance(expr, g.OrExpr):
                return self.eval(expr.left) or self.eval(expr.right)
            if isinstance(expr, g.NotExpr):
                return not self.eval(expr.expr)

            assert_never(expr)
        finally:
            self._depth -= 1

    def _eval_dot_path(self, dot_path: g.DotPath) -> bool:
        value = self._resolve_dot_path(dot_path)

        # Can't check for BoolExprDefinition (circular dep)
        if isinstance(value, BaseModel):
            try:
                maybe_bool_expr = cast("BoolExprDefinition", value).value
            except AttributeError:
                pass
            else:
                if isinstance(maybe_bool_expr, list):
                    return all(self.eval(ex) for ex in maybe_bool_expr)
                if isinstance(maybe_bool_expr, g.BoolExpr):
                    return self.eval(maybe_bool_expr)

        return bool(value)

    def _eval_arith(self, expr: g.ArithExpr) -> int | float:
        left = self._eval_numeric_operand(expr.left, expr.operator.value)
        right = self._eval_numeric_operand(expr.right, expr.operator.value)

        if expr.operator.value == "+":
            return left + right
        if expr.operator.value == "-":
            return left - right
        if expr.operator.value == "*":
            return left * right
        if expr.operator.value == "/":
            return left / right

        assert_never(expr.operator.value)

    def _eval_numeric_operand(self, operand: g.Expr, operator: str) -> int | float:
        """Evaluate an arithmetic operand, enforcing the numeric-only rule."""
        value = self.eval_value(operand)
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            msg = (
                f"Arithmetic operator '{operator}' requires numeric operands, "
                f"got {type(value).__name__}"
            )
            raise ExpressionEvalError(msg)
        return value

    def _eval_comparison(self, comp: g.Comparison) -> bool:
        left = self.resolve_comparison_operand(comp.left)
        right = self.resolve_comparison_operand(comp.right)
        op = comp.op.value

        # Identity/Equality (supports everything)
        if op == "==":
            return left == right
        if op == "!=":
            return left != right

        # Membership (requires collection on the right)
        if op == "in":
            if isinstance(right, (Sequence, str)) and not isinstance(right, (bool, int, float)):
                return left in right
            msg = f"Operator 'in' requires a collection, but got {type(right).__name__}"
            raise TypeError(msg)

        # Mathematical inequality (strictly NO entities or sequences)
        if isinstance(left, (BaseEntity, Sequence)) or isinstance(right, (BaseEntity, Sequence)):
            msg = f"Operands not supported for comparison '{op}'"
            raise TypeError(msg)

        if op == "<":
            return left < right
        if op == "<=":
            return left <= right
        if op == ">":
            return left > right
        if op == ">=":
            return left >= right

        assert_never(op)

    def resolve_comparison_operand(self, operand: g.Expr) -> EntityProperty:
        if isinstance(operand, g.Literal):
            return operand.value
        return self.eval_value(operand)

    def _resolve_dot_path(self, dot_path: g.DotPath) -> EntityProperty:
        entity = self._resolve_entity(dot_path.entity_id.value)

        # Resolve property to entity along property chain
        for prop_id in dot_path.property_chain[:-1]:
            prop = self._resolve_entity_property(entity, prop_id.value)
            if not isinstance(prop, BaseEntity):
                msg = f"Expected property {prop_id.value} on entity {entity.id} to be an entity"
                raise ExpressionEvalError(msg)
            entity = prop

        # Last prop ID in prop chain
        return self._resolve_entity_property(entity, dot_path.property_chain[-1].value)

    def _resolve_entity(self, entity_id: str) -> "BaseEntity":
        try:
            return self._project.get_entity(entity_id)
        except EntityNotFoundError as err:
            msg = f"Invalid entity ID: {entity_id}"
            raise ExpressionEvalError(msg) from err

    def _resolve_entity_property(self, entity: "BaseEntity", property_id: str) -> EntityProperty:
        if self._story_context is not None:
            with suppress(EntityFieldNotFoundError):
                effective = self._story_context.get_field(entity.id, property_id)
                if isinstance(effective, str | bool | int | float):
                    return effective
                return str(effective)

        is_model_field = property_id in entity.__class__.model_fields
        is_property = isinstance(getattr(entity.__class__, property_id, None), property)

        if is_model_field or is_property:
            return cast("EntityProperty", getattr(entity, property_id))

        msg = f"Property '{property_id}' not found on entity '{entity.id}'"
        raise ExpressionEvalError(msg)
