from collections.abc import Mapping
from typing import Any

from llm_gamebook.schema.expression import BooleanExpression
from llm_gamebook.story.entity import BaseStoryEntity
from llm_gamebook.story.traits.registry import trait


@trait("described")
class DescribedTrait(BaseStoryEntity):
    """Adds LLM-facing fields to an entity."""

    def __init__(
        self,
        name: str,
        description: str | None = None,
        *args: Any,
        enabled: BooleanExpression | None = None,
        **kwargs: Any,
    ):
        super().__init__(*args, **kwargs)
        self.name = name
        self.description = description
        self.enabled = enabled or BooleanExpression(value=True)

    def get_template_context(
        self, entities: "Mapping[str, BaseStoryEntity]"
    ) -> Mapping[str, object]:
        ctx = super().get_template_context(entities)
        return {
            **ctx,
            "name": self.name,
            "description": self.description,
            "enabled": self.enabled.evaluate(entities),
        }
