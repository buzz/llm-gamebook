from typing import TYPE_CHECKING, assert_never

from llm_gamebook.story.conditions.expression import (
    BoolExpr,
    BoolLiteral,
    Comparison,
    DotPath,
    FloatLiteral,
    IntLiteral,
    Literal,
    StrLiteral,
)
from llm_gamebook.story.entity import BaseStoryEntity

if TYPE_CHECKING:
    from collections.abc import Mapping

    from llm_gamebook.story.entity import EntityProperty


class ExpressionEvalError(Exception):
    """Raised when evaluation of an expression failed."""


def resolve_entity_property(entity: "BaseStoryEntity", property_id: str) -> "EntityProperty":
    # TODO: check property is in props model
    return getattr(entity, property_id)


def resolve_entity(entity_id: str, entities: "Mapping[str, BaseStoryEntity]") -> "BaseStoryEntity":
    try:
        return entities[entity_id]
    except KeyError as err:
        msg = f"Invalid entity ID: {entity_id}"
        raise ExpressionEvalError(msg) from err


def resolve_dot_path(
    dot_path: DotPath, entities: "Mapping[str, BaseStoryEntity]"
) -> "EntityProperty":
    entity = resolve_entity(dot_path.entity_id.value, entities)

    # Resolve property to entity along property chain
    for prop_id in dot_path.property_chain[:-1]:
        prop = resolve_entity_property(entity, prop_id.value)
        if not isinstance(prop, BaseStoryEntity):
            msg = f"Expected property {prop_id.value} on entity {entity.id} to be an entity"
            raise ExpressionEvalError(msg)
        entity = prop

    # Last prop ID in prop chain
    return resolve_entity_property(entity, dot_path.property_chain[-1].value)


def resolve_comparison_operand(
    operand: DotPath | Literal, entities: "Mapping[str, BaseStoryEntity]"
) -> "EntityProperty":
    return resolve_dot_path(operand, entities) if isinstance(operand, DotPath) else operand.value


def eval_comparison(comp: Comparison, entities: "Mapping[str, BaseStoryEntity]") -> bool:
    left = resolve_comparison_operand(comp.left, entities)
    right = resolve_comparison_operand(comp.right, entities)
    if comp.op.value == "==":
        return left == right

    return False


def eval_bool_expr(expr: BoolExpr, entities: "Mapping[str, BaseStoryEntity]") -> bool:
    # Literal
    if isinstance(expr, StrLiteral | IntLiteral | FloatLiteral | BoolLiteral):
        return bool(expr.value)

    if isinstance(expr, DotPath):
        return bool(resolve_dot_path(expr, entities))

    if isinstance(expr, Comparison):
        return eval_comparison(expr, entities)

    return False

    assert_never(expr)
