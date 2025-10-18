from collections.abc import Sequence
from typing import TYPE_CHECKING, assert_never

from llm_gamebook.story.conditions import bool_expr_grammar as g
from llm_gamebook.story.entity import BaseEntity
from llm_gamebook.story.errors import EntityNotFoundError

if TYPE_CHECKING:
    from llm_gamebook.story.entity import EntityProperty
    from llm_gamebook.story.project import Project


class ExpressionEvalError(Exception):
    """Raised when evaluation of an expression failed."""


class BoolExprEvaluator:
    def __init__(self, project: "Project") -> None:
        self._project = project

    def eval(self, expr: g.BoolExpr) -> bool:
        if isinstance(expr, g.Literal):
            return bool(expr.value)
        if isinstance(expr, g.DotPath):
            return bool(self._resolve_dot_path(expr))
        if isinstance(expr, g.Comparison):
            return self._eval_comparison(expr)
        if isinstance(expr, g.AndExpr):
            return self.eval(expr.left) and self.eval(expr.right)
        if isinstance(expr, g.OrExpr):
            return self.eval(expr.left) or self.eval(expr.right)
        if isinstance(expr, g.NotExpr):
            return not self.eval(expr.expr)

        assert_never(expr)

    def _eval_comparison(self, comp: g.Comparison) -> bool:
        left = self.resolve_comparison_operand(comp.left)
        right = self.resolve_comparison_operand(comp.right)
        op = comp.op.value

        if op == "==":
            return left == right
        if op == "!=":
            return left != right

        if isinstance(left, BaseEntity | Sequence):
            msg = f"Left operand '{left}' not supported for comparison '{op}'"
            raise TypeError(msg)
        if isinstance(right, BaseEntity | Sequence):
            msg = f"Right operand '{right}' not supported for comparison '{op}'"
            raise TypeError(msg)

        if op == "<":
            return left < right
        if op == "<=":
            return left <= right
        if op == ">":
            return left > right
        if op == ">=":
            return left >= right
        if op == "in":
            raise NotImplementedError

        assert_never(op)

    def resolve_comparison_operand(self, operand: g.DotPath | g.Literal) -> "EntityProperty":
        return self._resolve_dot_path(operand) if isinstance(operand, g.DotPath) else operand.value

    def _resolve_dot_path(self, dot_path: g.DotPath) -> "EntityProperty":
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

    def _resolve_entity_property(self, entity: "BaseEntity", property_id: str) -> "EntityProperty":
        # TODO: check property is in props model
        return getattr(entity, property_id)
