from typing import TYPE_CHECKING

from pydantic import Field

from llm_gamebook.schemas.expression import BoolExprDefinition
from llm_gamebook.story.conditions import bool_expr_grammar as g
from llm_gamebook.story.conditions.evaluator import BoolExprEvaluator
from llm_gamebook.story.schemas import BaseEntity
from llm_gamebook.story.trait_registry import session_field, trait_registry

if TYPE_CHECKING:
    from llm_gamebook.story.context import StoryContext


@trait_registry.register("described")
class DescribedTrait(BaseEntity):
    """Trait adding fields for LLM-facing data to an entity."""

    name: str
    """Human-readable name of the entity presented to the LLM."""

    description: str
    """Detailed description of the entity presented to the LLM."""

    enabled: BoolExprDefinition = Field(
        default_factory=lambda: BoolExprDefinition(value=g.BoolLiteral(value=True))
    )
    """If the entity should be presented to the LLM."""

    @session_field("enabled")
    def _resolve_enabled(self, story_context: "StoryContext") -> bool:
        """Resolve enabled field with session-aware evaluation."""
        evaluator = BoolExprEvaluator(story_context.project, story_context)
        return self.enabled.evaluate(story_context.project, evaluator)
