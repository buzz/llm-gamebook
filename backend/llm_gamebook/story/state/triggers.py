"""Trigger system: condition-based action dispatch after state changes (Stage 4)."""

import logging
from typing import TYPE_CHECKING, cast

from llm_gamebook.story.conditions.evaluator import BoolExprEvaluator, ExpressionEvalError
from llm_gamebook.story.conditions.grammar import parse_bool_expr
from llm_gamebook.story.schemas import TriggerDefinition

from .actions import Action, GenericPayload

if TYPE_CHECKING:
    from pydantic import BaseModel

    from llm_gamebook.story.context import StoryContext

    from .store import Store

logger = logging.getLogger(__name__)


def is_trigger_condition_true(context: "StoryContext", trigger: TriggerDefinition) -> bool:
    """Evaluate a trigger's condition against the current effective state.

    Args:
        context: The story context providing project and session state.
        trigger: The trigger whose condition to evaluate.

    Returns:
        True if the condition evaluates to true.

    Raises:
        ExpressionEvalError: If the condition cannot be parsed or evaluated.
    """
    try:
        condition = parse_bool_expr(trigger.condition)
    except ValueError as err:
        msg = f"Invalid trigger condition {trigger.condition!r}: {err}"
        raise ExpressionEvalError(msg) from err

    evaluator = BoolExprEvaluator(context.project, context)
    return evaluator.eval(condition)


def make_trigger_action(trigger: TriggerDefinition) -> "Action[BaseModel]":
    """Build the action a trigger dispatches (its name with args as payload)."""
    payload = GenericPayload.model_validate(trigger.args)
    return cast("Action[BaseModel]", Action[GenericPayload](name=trigger.name, payload=payload))


def dispatch_triggered_actions(store: "Store", context: "StoryContext") -> None:
    """Evaluate all project triggers and dispatch the actions that fire.

    Triggers are evaluated in YAML definition order against the committed
    state. A trigger whose action type was already dispatched in the current
    dispatch chain is skipped, preventing re-dispatch loops.

    Raises:
        ExpressionEvalError: If a trigger condition cannot be parsed or evaluated.
    """
    for entity_type in context.project.entity_type_map.values():
        for trigger in entity_type.triggers:
            if not is_trigger_condition_true(context, trigger):
                logger.debug("Trigger condition false for action '%s'", trigger.name)
                continue

            if trigger.name in store.active_action_types:
                logger.debug("Skipping trigger action '%s' (already dispatched)", trigger.name)
                continue

            logger.info("Trigger fired: dispatching '%s'", trigger.name)
            store.dispatch(make_trigger_action(trigger))
