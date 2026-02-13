from collections.abc import Mapping

from pydantic import Field

from llm_gamebook.schema.expression import BoolExprDefinition
from llm_gamebook.story.conditions import bool_expr_grammar as g
from llm_gamebook.story.entity import BaseEntity
from llm_gamebook.story.trait_registry import trait_registry


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

    def get_template_context(self) -> Mapping[str, object]:
        return {
            **super().get_template_context(),
            "name": self.name,
            "description": self.description,
            "enabled": self.enabled.evaluate(self.project),
        }
